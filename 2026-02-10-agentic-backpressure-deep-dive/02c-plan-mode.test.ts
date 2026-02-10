/**
 * Learning Test 02c: Three ways to restrict an agent
 *
 * Goal: build a read-only research agent that cannot modify files.
 *
 * We now know allowedTools is ignored (02) and disallowedTools works (02b).
 * But the SDK has two more mechanisms. Let's test all three side by side
 * and prove which ones actually restrict behavior.
 *
 * Structure:
 *   1. allowedTools: ['Read', 'Glob', 'Grep']  → does NOT restrict (02 proved this)
 *   2. disallowedTools: ['Write', 'Edit', ...]  → DOES restrict (02b proved this)
 *   3. permissionMode: 'plan'                   → DOES restrict (new finding)
 *
 * The assertions below are written to FAIL for the broken approach
 * and PASS for the working approaches. Flip them on stream to document reality.
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { query } from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(120_000);

describe("02c: Three ways to restrict an agent", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-02c-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	// Helper: run a query and return the available tools from system:init
	async function getAvailableTools(options: Record<string, any>): Promise<string[]> {
		let tools: string[] = [];
		for await (const message of query({
			prompt: "Say hello",
			options: {
				cwd: tempDir,
				maxTurns: 1,
				model: "haiku",
				...options,
			},
		})) {
			if (message.type === "system" && message.subtype === "init") {
				tools = message.tools;
			}
		}
		return tools;
	}

	test("allowedTools does NOT remove dangerous tools", async () => {
		const tools = await getAvailableTools({
			permissionMode: "default",
			allowedTools: ["Read", "Glob", "Grep"],
		});

		console.log("\n--- allowedTools: ['Read', 'Glob', 'Grep'] ---");
		console.log(`Write still available: ${tools.includes("Write")}`);
		console.log(`Bash still available:  ${tools.includes("Bash")}`);

		// FAILS: allowedTools doesn't work as a whitelist
		// flip to toBe(true) to document reality
		expect(tools.includes("Write")).toBe(false);
		expect(tools.includes("Bash")).toBe(false);
	});

	test("disallowedTools DOES remove dangerous tools", async () => {
		const tools = await getAvailableTools({
			permissionMode: "default",
			disallowedTools: ["Write", "Edit", "NotebookEdit", "Bash"],
		});

		console.log("\n--- disallowedTools: ['Write', 'Edit', 'NotebookEdit', 'Bash'] ---");
		console.log(`Write available: ${tools.includes("Write")}`);
		console.log(`Bash available:  ${tools.includes("Bash")}`);
		console.log(`Read available:  ${tools.includes("Read")}`);

		// PASSES: disallowedTools actually removes them
		expect(tools.includes("Write")).toBe(false);
		expect(tools.includes("Bash")).toBe(false);
		expect(tools.includes("Read")).toBe(true);
	});

	test("permissionMode: 'plan' DOES remove dangerous tools", async () => {
		const tools = await getAvailableTools({
			permissionMode: "plan",
		});

		console.log("\n--- permissionMode: 'plan' ---");
		console.log(`Write available: ${tools.includes("Write")}`);
		console.log(`Bash available:  ${tools.includes("Bash")}`);
		console.log(`Read available:  ${tools.includes("Read")}`);

		// PASSES: plan mode strips write tools entirely
		expect(tools.includes("Write")).toBe(false);
		expect(tools.includes("Edit")).toBe(false);
		expect(tools.includes("Read")).toBe(true);
	});
});
