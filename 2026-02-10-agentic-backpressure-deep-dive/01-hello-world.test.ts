/**
 * Learning Test 01: The Minimum Viable Learning Test
 *
 * Question: What does the Claude Agent SDK event stream actually look like?
 *           What events come back, in what order, and what's on each one?
 *
 * Key findings:
 * - query() returns an AsyncIterable of events
 * - First event is system:init, which gives you the session_id and available tools
 * - assistant events carry the model's response in message.content
 * - result:success is the final event, with the plaintext result
 * - session_id is consistent across all events in a session
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { query } from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(120_000);

describe("01: Hello World - Does this thing even work?", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-01-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("what events does query() emit, and in what order?", async () => {
		const events: Array<{ type: string; subtype?: string }> = [];
		let sessionId: string | undefined;
		let availableTools: string[] = [];
		let finalResult = "";

		const q = query({
			prompt: "Say hello",
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q) {
			const subtype = "subtype" in message ? (message.subtype as string) : undefined;
			events.push({ type: message.type, subtype });

			if (message.type === "system" && message.subtype === "init") {
				sessionId = message.session_id;
				availableTools = message.tools;
			}

			if (message.type === "result" && message.subtype === "success") {
				finalResult = message.result;
			}
		}

		// Log what we found - this is the Rosetta Stone
		console.log("\n--- Event Stream Shape ---");
		for (const e of events) {
			console.log(`  ${e.type}${e.subtype ? `:${e.subtype}` : ""}`);
		}
		console.log(`\nsession_id: ${sessionId}`);
		console.log(`available tools: ${availableTools.length} tools`);
		console.log(`final result: "${finalResult.substring(0, 80)}..."`);

		// Assertions: what we now know for sure
		expect(sessionId).toBeDefined();
		expect(typeof sessionId).toBe("string");
		expect(events[0]).toEqual({ type: "system", subtype: "init" });
		expect(events.some((e) => e.type === "assistant")).toBe(true);
		expect(events[events.length - 1]).toEqual({ type: "result", subtype: "success" });
		expect(finalResult.length).toBeGreaterThan(0);
	});

	test("session_id is consistent across all events", async () => {
		const sessionIds = new Set<string>();

		const q = query({
			prompt: "List 3 fruits",
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 2,
				model: "haiku",
			},
		});

		for await (const message of q) {
			if ("session_id" in message && message.session_id) {
				sessionIds.add(message.session_id);
			}
		}

		console.log(`\nUnique session_ids seen: ${sessionIds.size}`);
		expect(sessionIds.size).toBe(1);
	});
});
