/**
 * Step 3: Now let's collect events into arrays and check our assumptions.
 * This is the bridge to a real test -- we're accumulating data and
 * verifying it at the end, we just haven't added the test harness yet.
 *
 * Run it: bun run 00c-collect-and-check.ts
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

const events: Array<{ type: string; subtype?: string }> = [];
let sessionId: string | undefined;
let availableTools: string[] = [];
let finalResult = "";

for await (const message of query({
	prompt: "Say hello",
	options: {
		permissionMode: "bypassPermissions",
		allowedTools: [],
		maxTurns: 1,
		model: "haiku",
	},
})) {
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

// Now check what we learned
console.log("\n--- Event Stream Shape ---");
for (const e of events) {
	console.log(`  ${e.type}${e.subtype ? `:${e.subtype}` : ""}`);
}

console.log(`\nsession_id: ${sessionId}`);
console.log(`tools: ${availableTools.length}`);
console.log(`result: "${finalResult.substring(0, 80)}..."`);

// Manual checks -- these become assertions in 01
console.log("\n--- Checks ---");
console.log(`first event is system:init? ${events[0]?.type === "system" && events[0]?.subtype === "init"}`);
console.log(`has assistant event? ${events.some((e) => e.type === "assistant")}`);
console.log(`last event is result:success? ${events.at(-1)?.type === "result" && events.at(-1)?.subtype === "success"}`);
console.log(`got a session_id? ${sessionId !== undefined}`);
console.log(`got a result? ${finalResult.length > 0}`);
