/**
 * Learning Test 02b: OK so allowedTools doesn't work. What does?
 *
 * After 02 failed our assumption, we dig into the SDK types and find
 * `disallowedTools`. Let's test whether THAT actually removes tools.
 *
 * Key findings:
 * - disallowedTools is the real mechanism for restricting tool access
 * - It's a blocklist, not a whitelist (opposite mental model from allowedTools)
 * - Tools removed via disallowedTools are completely gone from the init event
 * - Read-only tools remain available when you only block write tools
 *
 * Updated understanding: to build a read-only research agent, use
 * disallowedTools: ['Write', 'Edit', 'NotebookEdit', 'Bash']
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { query } from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(120_000);

describe("02b: The fix - disallowedTools is the real mechanism", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-02b-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("disallowedTools actually removes tools from the available list", async () => {
		let availableTools: string[] = [];

		const q = query({
			prompt: "Say hello",
			options: {
				cwd: tempDir,
				permissionMode: "default",
				disallowedTools: ["Write", "Edit", "NotebookEdit", "Bash"],
				maxTurns: 1,
				model: "haiku",
			},
		});

		for await (const message of q) {
			if (message.type === "system" && message.subtype === "init") {
				availableTools = message.tools;
			}
		}

		console.log("\n--- disallowedTools: ['Write', 'Edit', 'NotebookEdit', 'Bash'] ---");
		console.log(`Write available: ${availableTools.includes("Write")}`);
		console.log(`Edit available:  ${availableTools.includes("Edit")}`);
		console.log(`Bash available:  ${availableTools.includes("Bash")}`);
		console.log(`Read available:  ${availableTools.includes("Read")}`);
		console.log(`Glob available:  ${availableTools.includes("Glob")}`);
		console.log(`Grep available:  ${availableTools.includes("Grep")}`);
		console.log(`Total tools:     ${availableTools.length}`);

		// The dangerous tools are actually gone
		expect(availableTools.includes("Write")).toBe(false);
		expect(availableTools.includes("Edit")).toBe(false);
		expect(availableTools.includes("Bash")).toBe(false);

		// Read-only tools are still there
		expect(availableTools.includes("Read")).toBe(true);
		expect(availableTools.includes("Glob")).toBe(true);
		expect(availableTools.includes("Grep")).toBe(true);

		console.log("\n=== FINDING ===");
		console.log("Use disallowedTools (blocklist), not allowedTools (ignored whitelist)");
		console.log("For a read-only agent: disallowedTools: ['Write', 'Edit', 'NotebookEdit', 'Bash']");
	});
});
