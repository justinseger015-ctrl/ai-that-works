/**
 * Learning Test 02: The Naive Assumption
 *
 * Question: I want a read-only research agent. The SDK has an `allowedTools`
 *           option. If I pass ['Read', 'Glob', 'Grep'], that should give me
 *           a read-only agent, right?
 *
 * Expected: Only Read, Glob, Grep are available. Write and Bash are gone.
 * Actual:   ...run it and find out.
 *
 * This is the test you'd write BEFORE building your multi-phase workflow.
 * It takes 30 seconds. The bug it prevents takes 2 hours.
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { query } from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(120_000);

describe("02: The naive assumption - allowedTools should be a whitelist", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-02-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("passing allowedTools: ['Read', 'Glob', 'Grep'] should restrict to read-only", async () => {
		let availableTools: string[] = [];

		const q = query({
			prompt: "Say hello",
			options: {
				cwd: tempDir,
				permissionMode: "default",
				allowedTools: ["Read", "Glob", "Grep"], // <-- this looks like a whitelist
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q) {
			if (message.type === "system" && message.subtype === "init") {
				availableTools = message.tools;
			}
		}

		console.log("\n--- What we expected ---");
		console.log("Only Read, Glob, Grep available");
		console.log("\n--- What actually happened ---");
		console.log(`Write available: ${availableTools.includes("Write")}`);
		console.log(`Bash available:  ${availableTools.includes("Bash")}`);
		console.log(`Edit available:  ${availableTools.includes("Edit")}`);
		console.log(`Total tools:     ${availableTools.length}`);

		// If allowedTools is a whitelist, these dangerous tools should be GONE:
		expect(availableTools.includes("Write")).toBe(false);  // should be gone... right?
		expect(availableTools.includes("Bash")).toBe(false);   // should be gone... right?
		expect(availableTools.includes("Edit")).toBe(false);   // should be gone... right?
	});
});
