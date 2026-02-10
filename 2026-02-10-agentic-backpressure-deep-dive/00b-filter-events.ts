/**
 * Step 2: OK, console.log(message) dumps a wall of JSON.
 * Let's filter by event type so we can see the structure.
 *
 * Run it: bun run 00b-filter-events.ts
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
	prompt: "Say hello",
	options: {
		permissionMode: "bypassPermissions",
		allowedTools: [],
		maxTurns: 1,
		model: "haiku",
	},
})) {
	const subtype = "subtype" in message ? message.subtype : undefined;
	console.log(`[${message.type}${subtype ? `:${subtype}` : ""}]`);

	if (message.type === "system" && message.subtype === "init") {
		console.log(`  session_id: ${message.session_id}`);
		console.log(`  tools: ${message.tools.join(", ")}`);
	}

	if (message.type === "assistant") {
		const text = message.message.content
			.filter((b: any) => b.type === "text")
			.map((b: any) => b.text)
			.join("");
		console.log(`  ${text.substring(0, 120)}`);
	}

	if (message.type === "result" && message.subtype === "success") {
		console.log(`  result: ${message.result.substring(0, 120)}`);
	}
}
