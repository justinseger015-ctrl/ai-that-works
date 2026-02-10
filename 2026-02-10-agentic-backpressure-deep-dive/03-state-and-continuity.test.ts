/**
 * Learning Test 03: Proving State Management Semantics
 *
 * Question: How does the SDK handle session continuity?
 *           What's the difference between resume, forkSession, and continue?
 *
 * Key findings:
 * - resume with session ID returns the SAME session_id and preserves context
 * - forkSession creates a NEW session_id but copies the full conversation history
 * - continue: true finds the most recent session in the cwd directory
 * - Each method has different implications for context isolation vs. sharing
 *
 * Why this matters: if you're chaining agent invocations in a workflow,
 * you need to know exactly which method preserves context, which creates
 * isolation, and which uses directory-based discovery.
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { query } from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(180_000);

describe("03: State and Continuity - How does this system remember?", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-03-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("resume: same session ID, preserves context", async () => {
		// Round 1: store a secret
		let originalSessionId: string | undefined;

		const q1 = query({
			prompt: "Remember this secret code: ZEBRA-9876. Just acknowledge.",
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q1) {
			if (message.type === "system" && message.subtype === "init") {
				originalSessionId = message.session_id;
			}
		}

		expect(originalSessionId).toBeDefined();

		// Round 2: retrieve it with resume
		let resumedSessionId: string | undefined;
		let result = "";

		const q2 = query({
			prompt: "What was the secret code I told you to remember?",
			options: {
				cwd: tempDir,
				resume: originalSessionId,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q2) {
			if (message.type === "system" && message.subtype === "init") {
				resumedSessionId = message.session_id;
			}
			if (message.type === "result" && message.subtype === "success") {
				result = message.result;
			}
		}

		console.log("\n--- Resume Test ---");
		console.log(`Original session: ${originalSessionId}`);
		console.log(`Resumed session:  ${resumedSessionId}`);
		console.log(`Same session ID:  ${resumedSessionId === originalSessionId}`);
		console.log(`Remembers secret: ${result.toLowerCase().includes("zebra") || result.includes("9876")}`);

		// resume = same session, same context
		expect(resumedSessionId).toBe(originalSessionId);
		expect(result.toLowerCase()).toMatch(/zebra|9876/);
	});

	test("forkSession: new session ID, but preserves conversation history", async () => {
		// Round 1: store a different secret
		let originalSessionId: string | undefined;

		const q1 = query({
			prompt: "Remember this code: ALPHA-1234. Just acknowledge.",
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q1) {
			if (message.type === "system" && message.subtype === "init") {
				originalSessionId = message.session_id;
			}
		}

		expect(originalSessionId).toBeDefined();

		// Round 2: fork the session
		let forkedSessionId: string | undefined;
		let result = "";

		const q2 = query({
			prompt: "What code did I tell you to remember?",
			options: {
				cwd: tempDir,
				resume: originalSessionId,
				forkSession: true,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q2) {
			if (message.type === "system" && message.subtype === "init") {
				forkedSessionId = message.session_id;
			}
			if (message.type === "result" && message.subtype === "success") {
				result = message.result;
			}
		}

		console.log("\n--- Fork Session Test ---");
		console.log(`Original session: ${originalSessionId}`);
		console.log(`Forked session:   ${forkedSessionId}`);
		console.log(`Different ID:     ${forkedSessionId !== originalSessionId}`);
		console.log(`Still remembers:  ${result.toLowerCase().includes("alpha") || result.includes("1234")}`);

		// fork = new session ID, but context is copied
		expect(forkedSessionId).not.toBe(originalSessionId);
		expect(result.toLowerCase()).toMatch(/alpha|1234/);
	});

	test("continue: true finds most recent session by directory", async () => {
		// Use an isolated directory so we don't pick up sessions from other tests
		const isolatedDir = await mkdtemp(join(tmpdir(), "learning-03-continue-"));

		try {
			// Round 1: create a session in this directory
			let firstSessionId: string | undefined;

			const q1 = query({
				prompt: "The magic word is ELEPHANT. Remember it.",
				options: {
					cwd: isolatedDir,
					permissionMode: "bypassPermissions",
					allowedTools: [],
					maxTurns: 1,
					model: "haiku",
				},
			});

			for await (const message of q1) {
				if (message.type === "system" && message.subtype === "init") {
					firstSessionId = message.session_id;
				}
			}

			// Round 2: continue (no session ID needed - finds by directory)
			let continuedSessionId: string | undefined;
			let result = "";

			const q2 = query({
				prompt: "What was the magic word?",
				options: {
					cwd: isolatedDir,
					continue: true, // <-- finds most recent session in this cwd
					permissionMode: "bypassPermissions",
					allowedTools: [],
					maxTurns: 1,
					model: "haiku",
				},
			});

			for await (const message of q2) {
				if (message.type === "system" && message.subtype === "init") {
					continuedSessionId = message.session_id;
				}
				if (message.type === "result" && message.subtype === "success") {
					result = message.result;
				}
			}

			console.log("\n--- Continue Test ---");
			console.log(`First session:     ${firstSessionId}`);
			console.log(`Continued session: ${continuedSessionId}`);
			console.log(`Same session:      ${continuedSessionId === firstSessionId}`);
			console.log(`Remembers word:    ${result.toLowerCase().includes("elephant")}`);

			// continue = same session, found by directory
			expect(continuedSessionId).toBe(firstSessionId);
			expect(result.toLowerCase()).toContain("elephant");
		} finally {
			await rm(isolatedDir, { recursive: true, force: true });
		}
	});
});
