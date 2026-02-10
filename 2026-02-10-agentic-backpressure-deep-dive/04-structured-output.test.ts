/**
 * Learning Test 04: Proving the Shape of Data In and Out
 *
 * Question: How does structured output actually work?
 *           Can you switch between structured and plaintext across turns?
 *
 * Key findings:
 * - outputFormat with json_schema returns structured_output on the result event
 * - Zod schema -> JSON Schema conversion works via z.toJSONSchema()
 * - structured_output is a parsed object, not a string - ready to validate
 * - You can resume a session and switch from structured to plaintext output
 * - The model retains memory of structured data even when responding in plaintext
 *
 * Why this matters: structured outputs are the foundation for using agent
 * responses as phase transitions in a workflow. The exit condition of one
 * phase becomes the input to the next.
 */

import { afterAll, beforeAll, describe, expect, setDefaultTimeout, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

setDefaultTimeout(180_000);

// Define a schema - this is what we expect the model to return
const PizzaOrderSchema = z.object({
	pizzas: z.array(
		z.object({
			size: z.string(),
			toppings: z.array(z.string()),
		}),
	),
});

// Convert to JSON Schema (strip $schema field the SDK doesn't need)
const { $schema: _$schema, ...pizzaJsonSchema } = z.toJSONSchema(PizzaOrderSchema);

describe("04: Structured Output - What's the real data shape?", () => {
	let tempDir: string;

	beforeAll(async () => {
		tempDir = await mkdtemp(join(tmpdir(), "learning-04-"));
	});

	afterAll(async () => {
		await rm(tempDir, { recursive: true, force: true });
	});

	test("outputFormat returns typed, parseable structured_output", async () => {
		let structuredOutput: unknown;

		const q = query({
			prompt: "I have 3 pizzas: one large pepperoni, one small veggie, one large potato and liver",
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 3,
				model: "haiku",
				outputFormat: {
					type: "json_schema",
					schema: pizzaJsonSchema,
				},
			},
		});

		for await (const message of q) {
			if (message.type === "result" && message.subtype === "success") {
				structuredOutput = (message as { structured_output?: unknown }).structured_output;
			}
		}

		console.log("\n--- Structured Output Test ---");
		console.log(`structured_output exists: ${structuredOutput !== undefined}`);
		console.log(`type: ${typeof structuredOutput}`);
		console.log(`raw: ${JSON.stringify(structuredOutput, null, 2)}`);

		// It's already parsed - not a string
		expect(structuredOutput).toBeDefined();

		// Validate against our Zod schema
		const parsed = PizzaOrderSchema.parse(structuredOutput);
		console.log(`Parsed ${parsed.pizzas.length} pizzas`);

		expect(parsed.pizzas.length).toBe(3);
		for (const pizza of parsed.pizzas) {
			expect(typeof pizza.size).toBe("string");
			expect(Array.isArray(pizza.toppings)).toBe(true);
		}
	});

	test("can switch from structured to plaintext across session turns", async () => {
		let sessionId: string | undefined;
		let structuredOutput: unknown;
		let plaintextResult: string | undefined;

		// Turn 1: structured output
		const q1 = query({
			prompt: "I have 3 pizzas: one large pepperoni, one small veggie, one large potato and liver",
			options: {
				cwd: tempDir,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 3,
				model: "haiku",
				outputFormat: {
					type: "json_schema",
					schema: pizzaJsonSchema,
				},
			},
		});

		for await (const message of q1) {
			if (message.type === "system" && message.subtype === "init") {
				sessionId = message.session_id;
			}
			if (message.type === "result" && message.subtype === "success") {
				structuredOutput = (message as { structured_output?: unknown }).structured_output;
			}
		}

		expect(sessionId).toBeDefined();
		const parsed = PizzaOrderSchema.parse(structuredOutput);
		expect(parsed.pizzas.length).toBe(3);

		// Turn 2: resume same session, but plaintext this time
		const q2 = query({
			prompt: "How many pizzas is that again?",
			options: {
				cwd: tempDir,
				resume: sessionId,
				permissionMode: "bypassPermissions",
				allowedTools: [],
				maxTurns: 3,
				model: "haiku",
				// no outputFormat = plaintext
			},
		});

		for await (const message of q2) {
			if (message.type === "result" && message.subtype === "success") {
				plaintextResult = message.result;
			}
		}

		console.log("\n--- Cross-Turn Test ---");
		console.log(`Turn 1 (structured): ${parsed.pizzas.length} pizzas parsed`);
		console.log(`Turn 2 (plaintext): "${plaintextResult?.substring(0, 80)}..."`);
		console.log(`Model remembers count: ${plaintextResult?.toLowerCase().match(/3|three/) !== null}`);

		// The model remembers the structured data even in plaintext mode
		expect(plaintextResult).toBeDefined();
		expect(plaintextResult!.toLowerCase()).toMatch(/3|three/);
	});
});
