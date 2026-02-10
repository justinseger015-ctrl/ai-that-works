/**
 * Learning Test 03: child_process.exec behavior
 *
 * Question: What does exec() actually give you on success and failure?
 *           What shell does it use? What's on the error object?
 *           How do stdout and stderr interact with exit codes?
 *
 * Key findings:
 * - exec() uses /bin/sh, NOT your user shell (zsh/bash). $0 confirms this.
 * - On error, the Error object carries .stdout AND .stderr as string properties.
 *   This is non-obvious -- you get output even on failure.
 * - .code is the numeric exit code (1, 127, etc.), not a string error code.
 * - stderr alone does NOT cause a rejection. Only non-zero exit code does.
 * - "command not found" = exit code 127 (POSIX standard).
 * - exec() is vulnerable to shell injection: semicolons in user input become
 *   command separators. Use execFile() or spawn() for untrusted input.
 * - timeout option sends SIGTERM (.killed=true, .signal="SIGTERM", .code=null).
 */

import { describe, expect, setDefaultTimeout, test } from "bun:test";
import { exec } from "node:child_process";

setDefaultTimeout(10_000);

// Promisified exec that preserves the full error shape
function execAsync(
	cmd: string,
	opts?: Parameters<typeof exec>[1],
): Promise<{ stdout: string; stderr: string }> {
	return new Promise((resolve, reject) => {
		exec(cmd, opts ?? {}, (error, stdout, stderr) => {
			if (error) {
				reject(Object.assign(error, { stdout, stderr }));
			} else {
				resolve({ stdout, stderr });
			}
		});
	});
}

describe("03: child_process.exec - What's really in that error?", () => {
	test("what shell does exec() use?", async () => {
		// exec runs commands in a shell. But which one?
		const { stdout } = await execAsync("echo $0");

		console.log("\n--- Shell identity ---");
		console.log(`  $0 reports: ${stdout.trim()}`);

		// On macOS/Linux, it should be /bin/sh (NOT your user's zsh/bash)
		expect(stdout.trim()).toContain("sh");
	});

	test("successful command: what's the shape of the result?", async () => {
		const result = await execAsync('echo "hello" && echo "world" >&2');

		console.log("\n--- Successful command result shape ---");
		console.log(`  typeof result: ${typeof result}`);
		console.log(`  keys: ${Object.keys(result).join(", ")}`);
		console.log(`  stdout: "${result.stdout.trim()}"`);
		console.log(`  stderr: "${result.stderr.trim()}"`);

		expect(result.stdout.trim()).toBe("hello");
		expect(result.stderr.trim()).toBe("world");
	});

	test("failed command (exit 1): what's on the error object?", async () => {
		let caughtError: any;

		try {
			await execAsync("echo 'some output' && echo 'some error' >&2 && exit 1");
		} catch (e) {
			caughtError = e;
		}

		console.log("\n--- Error object from exit 1 ---");
		console.log(`  error is Error: ${caughtError instanceof Error}`);
		console.log(`  error.message: "${caughtError.message?.substring(0, 80)}"`);
		console.log(`  error.code: ${caughtError.code}`);
		console.log(`  error.killed: ${caughtError.killed}`);
		console.log(`  error.signal: ${caughtError.signal}`);
		console.log(`  error.cmd: "${caughtError.cmd}"`);

		// THE KEY QUESTION: does the error object carry stdout and stderr?
		console.log(`  error.stdout: "${caughtError.stdout?.trim()}"`);
		console.log(`  error.stderr: "${caughtError.stderr?.trim()}"`);

		expect(caughtError).toBeInstanceOf(Error);
		expect(caughtError.code).toBe(1); // exit code, NOT an error string
		expect(caughtError.stdout.trim()).toBe("some output");
		expect(caughtError.stderr.trim()).toBe("some error");
	});

	test("does stderr WITHOUT a non-zero exit code cause an error?", async () => {
		// Many programs write to stderr for warnings but exit 0.
		// Does exec treat this as success or failure?
		let threw = false;
		let result: any;

		try {
			result = await execAsync("echo 'warning: something' >&2 && exit 0");
		} catch {
			threw = true;
		}

		console.log("\n--- stderr with exit 0 ---");
		console.log(`  threw: ${threw}`);
		console.log(`  stderr: "${result?.stderr?.trim()}"`);

		// Does stderr alone cause a rejection, or only non-zero exit?
		expect(threw).toBe(false);
		expect(result.stderr.trim()).toBe("warning: something");
	});

	test("command not found: what does the error look like?", async () => {
		let caughtError: any;

		try {
			await execAsync("definitely_not_a_real_command_12345");
		} catch (e) {
			caughtError = e;
		}

		console.log("\n--- Command not found error ---");
		console.log(`  error.code: ${caughtError.code}`);
		console.log(`  error.stderr: "${caughtError.stderr?.trim().substring(0, 100)}"`);
		console.log(`  error.killed: ${caughtError.killed}`);

		// Is the exit code 127 (standard "command not found") or something else?
		expect(caughtError.code).toBe(127);
		expect(caughtError.stderr).toContain("not found");
	});

	test("what happens with special characters in arguments?", async () => {
		// Since exec runs in a shell, special chars get interpreted.
		// This is the classic injection gotcha.
		const userInput = "hello; echo INJECTED";

		// UNSAFE: string interpolation into shell command
		const unsafeResult = await execAsync(`echo ${userInput}`);

		console.log("\n--- Shell injection via exec ---");
		console.log(`  intended to echo: "${userInput}"`);
		console.log(`  actual stdout: "${unsafeResult.stdout.trim()}"`);

		// Does the semicolon get interpreted as a command separator?
		const lines = unsafeResult.stdout.trim().split("\n");
		console.log(`  number of output lines: ${lines.length}`);
		console.log(`  line 1: "${lines[0]}"`);
		console.log(`  line 2: "${lines[1] ?? "(none)"}"`);

		// This PROVES that exec is vulnerable to injection
		expect(lines.length).toBe(2);
		expect(lines[0]).toBe("hello");
		expect(lines[1]).toBe("INJECTED");
	});

	test("exec with timeout: what happens when the command takes too long?", async () => {
		let caughtError: any;

		try {
			await execAsync("sleep 10", { timeout: 500 });
		} catch (e) {
			caughtError = e;
		}

		console.log("\n--- exec with timeout ---");
		console.log(`  error.killed: ${caughtError.killed}`);
		console.log(`  error.signal: ${caughtError.signal}`);
		console.log(`  error.code: ${caughtError.code}`);

		// Does it get killed? With what signal? What's the exit code?
		expect(caughtError.killed).toBe(true);
		expect(caughtError.signal).toBe("SIGTERM");
	});
});
