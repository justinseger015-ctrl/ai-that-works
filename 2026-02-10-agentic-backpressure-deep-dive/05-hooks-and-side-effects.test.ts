/**
 * Learning Test 05: Testing Behavioral Injection and Side Effects
 *
 * Question: When do hooks fire, what data do they receive,
 *           and what happens to the data you return?
 *
 * Key findings:
 * - PostToolUse hooks receive tool_input (with file_path, content, etc.)
 *   and tool_response after tool execution
 * - PreToolUse hooks can block execution with { continue: false, decision: 'block' }
 * - Hooks can inject systemMessage to add context for the model
 * - SURPRISE: systemMessage is injected into the model's context but is
 *   NOT emitted as a separate event in the query() stream
 * - If you need to log/track systemMessages, you must do it inside the hook
 * - matcher is a regex pattern that filters which tools trigger the hook
 *
 * This is the kind of finding you'd never get from docs alone.
 * The systemMessage behavior is critical for building monitoring systems.
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { existsSync } from "node:fs";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
	type HookCallback,
	type HookInput,
	query,
} from "@anthropic-ai/claude-agent-sdk";

setDefaultTimeout(120_000);

describe("05: Hooks and Side Effects - What really happens at runtime?", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-05-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("PostToolUse hook captures tool_input and tool_response", async () => {
		const hookCalls: Array<{
			toolName: string;
			toolInput: unknown;
			toolResponse: unknown;
			filePath: string | undefined;
		}> = [];

		const captureHook: HookCallback = async (input, _toolUseID, _options) => {
			if (input.hook_event_name === "PostToolUse") {
				const toolInput = input.tool_input as { file_path?: string } | undefined;
				hookCalls.push({
					toolName: input.tool_name,
					toolInput: input.tool_input,
					toolResponse: input.tool_response,
					filePath: toolInput?.file_path,
				});
			}
			return { continue: true };
		};

		const testFile = join(tempDir, "hook-test.txt");

		const q = query({
			prompt: `Write "hello from hooks test" to ${testFile}`,
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowDangerouslySkipPermissions: true,
				maxTurns: 3,
				model: "haiku",
				hooks: {
					PostToolUse: [
						{
							matcher: "Write|Edit|MultiEdit",
							timeout: 30,
							hooks: [captureHook],
						},
					],
				},
			},
		});

		for await (const _message of q) {
			// consume
		}

		const writeCall = hookCalls.find((h) => h.toolName === "Write");

		console.log("\n--- PostToolUse Capture Test ---");
		console.log(`Hook calls: ${hookCalls.length}`);
		console.log(`Write captured: ${writeCall !== undefined}`);
		console.log(`file_path: ${writeCall?.filePath}`);
		console.log(`has tool_response: ${writeCall?.toolResponse !== undefined}`);
		console.log(`File exists: ${existsSync(testFile)}`);

		expect(hookCalls.length).toBeGreaterThan(0);
		expect(writeCall).toBeDefined();
		expect(writeCall?.filePath).toContain("hook-test.txt");
		expect(existsSync(testFile)).toBe(true);
	});

	test("PreToolUse hook can block tool execution", async () => {
		const blockedCalls: string[] = [];

		const blockingHook: HookCallback = async (input, _toolUseID, _options) => {
			if (input.hook_event_name !== "PreToolUse") {
				return { continue: true };
			}

			const toolInput = input.tool_input as { file_path?: string } | undefined;
			if (toolInput?.file_path?.includes("blocked")) {
				blockedCalls.push(input.tool_name);
				return {
					continue: false,
					decision: "block",
					reason: "Writes to blocked paths are not allowed",
				};
			}

			return { continue: true };
		};

		const blockedFile = join(tempDir, "blocked-file.txt");

		const q = query({
			prompt: `Write "test" to ${blockedFile}. If that fails, just say "write was blocked".`,
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowDangerouslySkipPermissions: true,
				maxTurns: 3,
				model: "haiku",
				hooks: {
					PreToolUse: [
						{
							matcher: "Write|Edit",
							hooks: [blockingHook],
						},
					],
				},
			},
		});

		for await (const _message of q) {
			// consume
		}

		console.log("\n--- PreToolUse Block Test ---");
		console.log(`Blocked calls: ${blockedCalls.join(", ")}`);
		console.log(`File exists: ${existsSync(blockedFile)}`);

		expect(blockedCalls.length).toBeGreaterThan(0);
		expect(existsSync(blockedFile)).toBe(false);
	});

	test("systemMessage is injected into context but NOT emitted as event", async () => {
		let hookFired = false;
		const allEvents: Array<{ type: string; subtype?: string; data: unknown }> = [];

		const messageHook: HookCallback = async (input, _toolUseID, _options) => {
			if (input.hook_event_name === "PostToolUse" && input.tool_name === "Write") {
				hookFired = true;
				return {
					continue: true,
					systemMessage: "[SYNC] File has been automatically synced to remote repository.",
				};
			}
			return { continue: true };
		};

		const testFile = join(tempDir, "message-test.txt");

		const q = query({
			prompt: `Write "test" to ${testFile}`,
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowDangerouslySkipPermissions: true,
				maxTurns: 3,
				model: "haiku",
				hooks: {
					PostToolUse: [
						{
							matcher: "Write",
							hooks: [messageHook],
						},
					],
				},
			},
		});

		for await (const message of q) {
			const subtype = "subtype" in message ? (message.subtype as string) : undefined;
			allEvents.push({ type: message.type, subtype, data: message });
		}

		// Search for our systemMessage text in ANY event
		const eventsWithMessage = allEvents.filter((e) =>
			JSON.stringify(e.data).includes("automatically synced"),
		);

		console.log("\n--- systemMessage Visibility Test ---");
		console.log(`Hook fired: ${hookFired}`);
		console.log(`Total events: ${allEvents.length}`);
		console.log(`Events containing systemMessage text: ${eventsWithMessage.length}`);
		console.log(`Event types: ${[...new Set(allEvents.map((e) => `${e.type}${e.subtype ? `:${e.subtype}` : ""}`))].join(", ")}`);

		// THE SURPRISE: systemMessage goes to the model but not to you
		expect(hookFired).toBe(true);
		expect(eventsWithMessage.length).toBe(0);

		console.log("\n=== KEY FINDING ===");
		console.log("systemMessage is injected into the model's context");
		console.log("but does NOT appear in the query() event stream.");
		console.log("If you need to log it, do it inside the hook callback.");
	});
});
