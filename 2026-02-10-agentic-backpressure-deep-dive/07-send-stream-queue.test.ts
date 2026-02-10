/**
 * Learning Test 07: V2 Send/Stream Separation and Message Queue Behavior
 *
 * Question: The V2 SDK separates send() and stream() into distinct steps.
 *           What happens if you delay between them? What if you send()
 *           twice before streaming? Does the queue back up? Does it drop?
 *           How does multi-turn actually work with this split?
 *
 * Key findings:
 * - Basic send/stream works as expected: send dispatches, stream yields events
 * - Event shape is identical to V1: system:init -> assistant(s) -> result:success
 * - Multi-turn preserves context: same session ID, model remembers prior turns
 * - Delayed stream: response is BUFFERED. A 3s delay between send() and stream()
 *   does NOT lose data. The agent processes during the delay, stream just picks it up.
 * - Double send: does NOT throw, but second message REPLACES the first (not queued).
 *   Only the first message was seen by the model. This is NOT a FIFO queue.
 * - unstable_v2_prompt: clean one-shot, returns SDKResultMessage directly
 * - Interleaved processing: the key win of V2 - arbitrary logic between turns
 *   without restructuring your code into generator coordination
 *
 * Why this matters: the V2 API's send/stream split is the foundation for
 * building workflows with logic between turns. The buffered-but-not-queued
 * semantics mean you MUST drain stream() before calling send() again, or
 * the earlier message context may be lost.
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
	unstable_v2_createSession,
	unstable_v2_prompt,
	type SDKMessage,
} from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(180_000);

// Helper to extract text from assistant messages
function getAssistantText(msg: SDKMessage): string | null {
	if (msg.type !== "assistant") return null;
	return msg.message.content
		.filter((block: { type: string }) => block.type === "text")
		.map((block: { type: string; text?: string }) => block.text ?? "")
		.join("");
}

// Helper to collect all text from a stream
async function drainStream(
	stream: AsyncGenerator<SDKMessage, void>,
): Promise<{ texts: string[]; events: Array<{ type: string; subtype?: string }>; sessionId?: string }> {
	const texts: string[] = [];
	const events: Array<{ type: string; subtype?: string }> = [];
	let sessionId: string | undefined;

	for await (const msg of stream) {
		const subtype = "subtype" in msg ? (msg.subtype as string) : undefined;
		events.push({ type: msg.type, subtype });

		if ("session_id" in msg && msg.session_id) {
			sessionId = msg.session_id;
		}

		const text = getAssistantText(msg);
		if (text) texts.push(text);
	}

	return { texts, events, sessionId };
}

describe("07: V2 Send/Stream - Message Queue and Backpressure", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-07-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("basic send/stream cycle: does the simplest V2 pattern work?", async () => {
		const session = unstable_v2_createSession({
			model: "haiku",
			permissionMode: "plan",
		});

		try {
			await session.send("What is 2 + 2? Reply with just the number.");

			const { texts, events, sessionId } = await drainStream(session.stream());

			console.log("\n--- Basic Send/Stream ---");
			console.log(`Session ID: ${sessionId}`);
			console.log(`Events: ${events.map((e) => `${e.type}${e.subtype ? `:${e.subtype}` : ""}`).join(", ")}`);
			console.log(`Response: "${texts.join("").substring(0, 80)}"`);

			expect(sessionId).toBeDefined();
			expect(texts.length).toBeGreaterThan(0);
			expect(texts.join("").toLowerCase()).toMatch(/4/);
			expect(events[0]).toEqual({ type: "system", subtype: "init" });
			expect(events[events.length - 1]).toEqual({ type: "result", subtype: "success" });
		} finally {
			session.close();
		}
	});

	test("multi-turn: send/stream/send/stream preserves conversation context", async () => {
		const session = unstable_v2_createSession({
			model: "haiku",
			permissionMode: "plan",
		});

		try {
			// Turn 1: establish a fact
			await session.send("Remember this: the password is MANGO-42. Just acknowledge.");
			const turn1 = await drainStream(session.stream());

			console.log("\n--- Multi-Turn: Turn 1 ---");
			console.log(`Response: "${turn1.texts.join("").substring(0, 80)}"`);

			// Turn 2: recall the fact
			await session.send("What was the password I told you?");
			const turn2 = await drainStream(session.stream());

			console.log("\n--- Multi-Turn: Turn 2 ---");
			console.log(`Response: "${turn2.texts.join("").substring(0, 80)}"`);
			console.log(`Same session: ${turn1.sessionId === turn2.sessionId}`);
			console.log(`Remembers password: ${turn2.texts.join("").includes("MANGO") || turn2.texts.join("").includes("42")}`);

			// Session ID persists across turns
			expect(turn2.sessionId).toBe(turn1.sessionId);
			// Context is preserved
			expect(turn2.texts.join("")).toMatch(/MANGO|42/);
		} finally {
			session.close();
		}
	});

	test("delayed stream: what if you wait before calling stream()?", async () => {
		const session = unstable_v2_createSession({
			model: "haiku",
			permissionMode: "plan",
		});

		try {
			await session.send("Say the word 'PINEAPPLE' and nothing else.");

			// Intentional delay - does the response wait for us?
			const delayMs = 3000;
			console.log(`\n--- Delayed Stream (${delayMs}ms delay) ---`);
			const sendTime = Date.now();
			await new Promise((resolve) => setTimeout(resolve, delayMs));
			const streamStartTime = Date.now();

			const { texts, events } = await drainStream(session.stream());
			const streamEndTime = Date.now();

			const actualDelay = streamStartTime - sendTime;
			const streamDuration = streamEndTime - streamStartTime;

			console.log(`Delay before stream(): ${actualDelay}ms`);
			console.log(`Stream duration: ${streamDuration}ms`);
			console.log(`Events: ${events.length}`);
			console.log(`Response: "${texts.join("").substring(0, 80)}"`);

			// The response should still arrive - it shouldn't be lost
			expect(texts.length).toBeGreaterThan(0);
			expect(texts.join("").toUpperCase()).toContain("PINEAPPLE");

			console.log("\n=== FINDING ===");
			console.log("Response is buffered - delay between send() and stream() does not lose data.");
			console.log(`Stream duration after ${actualDelay}ms delay: ${streamDuration}ms`);
		} finally {
			session.close();
		}
	});

	test("double send before stream: what happens to queued messages?", async () => {
		const session = unstable_v2_createSession({
			model: "haiku",
			permissionMode: "plan",
		});

		try {
			// Send two messages before streaming either response
			await session.send("The first number is 7.");

			// Does this throw? Block? Queue? Overwrite?
			let secondSendError: Error | null = null;
			try {
				await session.send("The second number is 13.");
			} catch (e) {
				secondSendError = e as Error;
			}

			console.log("\n--- Double Send Before Stream ---");
			console.log(`Second send threw: ${secondSendError !== null}`);
			if (secondSendError) {
				console.log(`Error: ${secondSendError.message}`);
			}

			// Stream whatever is available
			const { texts, events } = await drainStream(session.stream());
			console.log(`Events: ${events.length}`);
			console.log(`Response: "${texts.join("").substring(0, 120)}"`);

			const combined = texts.join("").toLowerCase();
			const knows7 = combined.includes("7");
			const knows13 = combined.includes("13");
			console.log(`Knows first number (7): ${knows7}`);
			console.log(`Knows second number (13): ${knows13}`);

			if (secondSendError) {
				console.log("\n=== FINDING ===");
				console.log("Double send() throws - you MUST stream() between sends.");
				console.log(`Error: ${secondSendError.message}`);
			} else {
				console.log("\n=== FINDING ===");
				console.log("Double send() succeeded - messages were queued.");
				console.log(`Both numbers remembered: ${knows7 && knows13}`);
			}

			// At minimum, the stream should produce something
			expect(events.length).toBeGreaterThan(0);
		} finally {
			session.close();
		}
	});

	test("unstable_v2_prompt: one-shot convenience vs session lifecycle", async () => {
		// Compare one-shot prompt to session-based approach
		const result = await unstable_v2_prompt(
			"What is 10 * 10? Reply with just the number.",
			{
				model: "haiku",
				permissionMode: "plan",
			},
		);

		console.log("\n--- One-Shot Prompt ---");
		console.log(`Result type: ${result.type}`);
		console.log(`Result subtype: ${"subtype" in result ? result.subtype : "n/a"}`);
		console.log(`Result text: "${(result as { result?: string }).result?.substring(0, 80)}"`);
		console.log(`Session ID: ${result.session_id}`);

		expect(result.type).toBe("result");
		expect("subtype" in result && result.subtype).toBe("success");
		expect((result as { result?: string }).result).toMatch(/100/);
	});

	test("interleaved processing: doing work between send and stream", async () => {
		// This is the key use case: run business logic between turns
		const session = unstable_v2_createSession({
			model: "haiku",
			permissionMode: "plan",
		});

		const processingLog: Array<{ step: string; timestamp: number }> = [];
		const startTime = Date.now();
		const log = (step: string) => processingLog.push({ step, timestamp: Date.now() - startTime });

		try {
			// Turn 1: ask for structured data
			log("send-turn1");
			await session.send("List exactly 3 colors: red, blue, green. One per line, nothing else.");
			log("send-turn1-done");

			// Simulate processing work BEFORE consuming the stream
			log("processing-before-stream");
			await new Promise((resolve) => setTimeout(resolve, 1000));
			log("processing-done");

			// Now consume
			log("stream-turn1-start");
			const turn1 = await drainStream(session.stream());
			log("stream-turn1-done");

			// Do more processing with the result
			const colors = turn1.texts.join("").split("\n").filter((l) => l.trim().length > 0);
			log(`parsed-colors: ${colors.length}`);

			// Turn 2: reference the previous output
			log("send-turn2");
			await session.send(`You listed ${colors.length} colors. Which one comes first alphabetically?`);
			log("send-turn2-done");

			log("stream-turn2-start");
			const turn2 = await drainStream(session.stream());
			log("stream-turn2-done");

			console.log("\n--- Interleaved Processing Timeline ---");
			for (const entry of processingLog) {
				console.log(`  +${entry.timestamp}ms: ${entry.step}`);
			}
			console.log(`\nTurn 1 response: "${turn1.texts.join("").substring(0, 80)}"`);
			console.log(`Turn 2 response: "${turn2.texts.join("").substring(0, 80)}"`);

			// The workflow completed without errors
			expect(turn1.texts.length).toBeGreaterThan(0);
			expect(turn2.texts.length).toBeGreaterThan(0);
			// Blue comes first alphabetically
			expect(turn2.texts.join("").toLowerCase()).toContain("blue");

			console.log("\n=== FINDING ===");
			console.log("The send/stream split allows arbitrary processing between turns.");
			console.log("This is the key advantage over V1's single async generator pattern.");
		} finally {
			session.close();
		}
	});
});
