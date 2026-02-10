/**
 * The simplest possible Claude Agent SDK script.
 *
 * This is what it looks like to run a coding agent programmatically.
 * One import, one function call, one for-await loop.
 *
 * Run it: bun run 00-sdk-basics.ts
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and read the meta.md and tell me whats there",
  options: { allowedTools: ["Read", "Edit", "Bash"] },
})) {
  console.log(message);
}
