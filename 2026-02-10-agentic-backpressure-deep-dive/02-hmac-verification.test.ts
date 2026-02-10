/**
 * Learning Test 02: HMAC Verification with node:crypto
 *
 * Question: How does HMAC signing and verification actually work in Node?
 *           What happens when timingSafeEqual gets mismatched lengths?
 *           What encoding does digest() return by default?
 *
 * Key findings:
 * - digest() returns a Buffer by default (not a string). SHA-256 = 32 bytes.
 * - digest("hex") returns a string; matches buffer.toString("hex") exactly.
 * - timingSafeEqual THROWS (ERR_CRYPTO_TIMING_SAFE_EQUAL_LENGTH) on length mismatch.
 *   It does NOT return false. This breaks naive webhook verification code.
 * - You MUST check lengths before calling timingSafeEqual, or wrap it in try/catch.
 * - The safe pattern: compare lengths first, return false on mismatch, then timingSafeEqual.
 */

import { describe, expect, setDefaultTimeout, test } from "bun:test";
import { createHmac, timingSafeEqual } from "node:crypto";

setDefaultTimeout(10_000);

describe("02: HMAC Verification - node:crypto gotchas", () => {
	const SECRET = "webhook-secret-key";
	const PAYLOAD = '{"event":"payment.completed","amount":4200}';

	test("what does createHmac().digest() return by default (no encoding arg)?", () => {
		const hmac = createHmac("sha256", SECRET);
		hmac.update(PAYLOAD);
		const result = hmac.digest();

		console.log("\n--- digest() default return type ---");
		console.log(`  typeof result: ${typeof result}`);
		console.log(`  result instanceof Buffer: ${result instanceof Buffer}`);
		console.log(`  result.length: ${result.length}`);
		console.log(`  result (hex): ${result.toString("hex")}`);

		// What is it? A Buffer? A string? Something else?
		expect(result).toBeInstanceOf(Buffer);
		expect(result.length).toBe(32); // SHA-256 = 32 bytes
	});

	test("digest('hex') vs digest() -- are they interchangeable for comparison?", () => {
		const sign = (payload: string) => {
			return createHmac("sha256", SECRET).update(payload).digest("hex");
		};

		const signBuffer = (payload: string) => {
			return createHmac("sha256", SECRET).update(payload).digest();
		};

		const hexSig = sign(PAYLOAD);
		const bufSig = signBuffer(PAYLOAD);

		console.log("\n--- hex string vs Buffer ---");
		console.log(`  hex string: ${hexSig}`);
		console.log(`  buffer as hex: ${bufSig.toString("hex")}`);
		console.log(`  are they equal? ${hexSig === bufSig.toString("hex")}`);

		expect(hexSig).toBe(bufSig.toString("hex"));
	});

	test("timingSafeEqual: what happens with MATCHING signatures?", () => {
		const sig1 = createHmac("sha256", SECRET).update(PAYLOAD).digest();
		const sig2 = createHmac("sha256", SECRET).update(PAYLOAD).digest();

		const result = timingSafeEqual(sig1, sig2);

		console.log("\n--- timingSafeEqual with matching sigs ---");
		console.log(`  result: ${result}`);
		console.log(`  typeof result: ${typeof result}`);

		expect(result).toBe(true);
	});

	test("timingSafeEqual: what happens with WRONG signature (same length)?", () => {
		const real = createHmac("sha256", SECRET).update(PAYLOAD).digest();
		const fake = createHmac("sha256", "wrong-key").update(PAYLOAD).digest();

		console.log("\n--- timingSafeEqual with wrong sig (same length) ---");
		console.log(`  real.length: ${real.length}, fake.length: ${fake.length}`);

		const result = timingSafeEqual(real, fake);
		console.log(`  result: ${result}`);

		expect(result).toBe(false);
	});

	test("timingSafeEqual: what happens with DIFFERENT LENGTH inputs?", () => {
		// This is the gotcha. Many webhook verification tutorials do:
		//   timingSafeEqual(Buffer.from(expected), Buffer.from(received))
		// But if an attacker sends a truncated signature, what happens?

		const real = createHmac("sha256", SECRET).update(PAYLOAD).digest();
		const truncated = real.subarray(0, 16); // half the bytes

		console.log("\n--- timingSafeEqual with different lengths ---");
		console.log(`  real.length: ${real.length}`);
		console.log(`  truncated.length: ${truncated.length}`);

		let threw = false;
		let errorMessage = "";
		try {
			timingSafeEqual(real, truncated);
		} catch (e: any) {
			threw = true;
			errorMessage = e.message;
			console.log(`  threw: ${threw}`);
			console.log(`  error.message: "${errorMessage}"`);
			console.log(`  error.code: ${e.code}`);
		}

		// Does it return false, or does it THROW?
		// This is critical for webhook verification code.
		expect(threw).toBe(true);
		expect(errorMessage).toContain("same byte length");
	});

	test("realistic webhook verification: the safe pattern vs the naive pattern", () => {
		// Simulate: server signs a payload, client sends signature in header
		const serverSign = (payload: string, secret: string): string => {
			return createHmac("sha256", secret).update(payload).digest("hex");
		};

		const expectedSig = serverSign(PAYLOAD, SECRET);

		// NAIVE verification (vulnerable to length mismatch throw)
		const naiveVerify = (payload: string, receivedSig: string, secret: string): boolean => {
			const expected = createHmac("sha256", secret).update(payload).digest("hex");
			return timingSafeEqual(Buffer.from(expected), Buffer.from(receivedSig));
		};

		// SAFE verification (handles length mismatch)
		const safeVerify = (payload: string, receivedSig: string, secret: string): boolean => {
			const expected = createHmac("sha256", secret).update(payload).digest("hex");
			const received = Buffer.from(receivedSig);
			const expectedBuf = Buffer.from(expected);

			if (received.length !== expectedBuf.length) {
				return false;
			}
			return timingSafeEqual(expectedBuf, received);
		};

		// Happy path: both work
		expect(naiveVerify(PAYLOAD, expectedSig, SECRET)).toBe(true);
		expect(safeVerify(PAYLOAD, expectedSig, SECRET)).toBe(true);

		// Attacker sends truncated sig: naive THROWS, safe returns false
		const truncatedSig = expectedSig.substring(0, 32);
		console.log("\n--- Naive vs Safe verification with truncated sig ---");

		let naiveThrew = false;
		try {
			naiveVerify(PAYLOAD, truncatedSig, SECRET);
		} catch {
			naiveThrew = true;
		}
		console.log(`  naive verify threw: ${naiveThrew}`);
		console.log(`  safe verify returned: ${safeVerify(PAYLOAD, truncatedSig, SECRET)}`);

		expect(naiveThrew).toBe(true);
		expect(safeVerify(PAYLOAD, truncatedSig, SECRET)).toBe(false);

		// Attacker sends empty string: naive THROWS, safe returns false
		let naiveThrewEmpty = false;
		try {
			naiveVerify(PAYLOAD, "", SECRET);
		} catch {
			naiveThrewEmpty = true;
		}
		console.log(`  naive verify (empty string) threw: ${naiveThrewEmpty}`);
		console.log(`  safe verify (empty string) returned: ${safeVerify(PAYLOAD, "", SECRET)}`);

		expect(naiveThrewEmpty).toBe(true);
		expect(safeVerify(PAYLOAD, "", SECRET)).toBe(false);
	});
});
