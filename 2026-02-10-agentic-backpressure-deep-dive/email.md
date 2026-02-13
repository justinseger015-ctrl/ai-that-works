Hello {firstName},

This week's 🦄 ai that works session explored learning tests and proof-driven development for AI coding agents.

The full recording is now on [YouTube](https://www.youtube.com/watch?v=Zx_GOhGik0o), and all the code is available on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-02-10-agentic-backpressure-deep-dive).

We've talked before about agentic backpressure—building feedback loops that help coding agents validate their assumptions and catch mistakes early. This week we went deeper into a specific technique: learning tests. When you're integrating with external APIs, CLIs, or any system you don't control, documentation only tells you so much. You need to actually poke the system and see what it does.

**Actions you can take today:**

**Write learning tests before building.** When your agent needs to call an unfamiliar API or CLI tool, have it write a small test program first that confirms the actual behavior. For example, if you're calling a payment API, write a test that hits the sandbox endpoint and validates the response structure. You'll catch documentation mismatches and edge cases before they blow up your implementation.

**Let your agent generate and run its own tests.** The real power move is having Claude Code (or your coding agent) write these learning tests itself, execute them, and update its understanding based on the results. When the test fails, the agent sees the actual error message and can correct its mental model without you having to intervene.

**Use proof-driven development for external integrations.** Before building the full feature, create small proof-of-concept programs that validate your core assumptions about how the external system works. This is especially valuable when integrating with systems that have spotty docs, unusual behavior, or complex authentication flows.

**If you remember one thing from this session:**

The fastest way to improve coding agent results is to give them concrete feedback loops. Learning tests let your agent check its assumptions against reality and self-correct before it writes production code—which means you spend less time debugging and more time shipping.

**Tomorrow's session: AI Content Pipeline Revisited**

Tomorrow, we're going meta again! This time we're walking through the entire pipeline we use to create each episode of this podcast. We'll show you the tools, the workflows, and the specific techniques we use to make AI-generated content not sound like AI slop. Expect browser agents, clip extraction, image generation, and a discussion about how far automation should actually go.

Sign up here: https://luma.com/ai-content-generation

If you have questions, reply to this email or ask on [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
