Hello {firstName},

This week's 🦄 ai that works session explored how prompting is moving from backend strings to user-facing product features.

The full recording is now on [YouTube](https://www.youtube.com/watch?v=qdfwmYTO0Aw), and all the code is available on [GitHub](https://github.com/hellovai/ai-that-works/tree/main/2026-02-03-prompting-is-becoming-a-product-surface).

We built a live system that translates user-friendly UI controls (dropdowns, checkboxes, text inputs) into structured prompts that LLMs can actually use. The core idea: your users want to say "give me bullet points" or "set temperature to Fahrenheit," not debug prompt syntax. So you need a translation layer that turns their intent into precise schema definitions.

**Actions you can take today:**

**Build a translation layer between UI and prompts.** When users select "bullet points" from a dropdown, your system should translate that into a structured schema (like a TypeScript type or Python class) that defines what the LLM should return. Users get simple controls; your prompt gets type safety. We showed this live by dynamically generating BAML schemas from UI selections.

**Separate display logic from LLM logic.** Include display-specific fields in your schema (like `units: "fahrenheit"` or `format: "bulleted"`) that influence how you render the output but don't get sent to the LLM. This lets you optimize both the prompt quality and the user experience independently.

**Let users customize without breaking your system.** Instead of giving users a raw prompt textarea, give them structured controls that map to known schema patterns. When they want bullets, you control how that translates into JSON schema. This keeps their customization safe while still feeling flexible.

**If you remember one thing from this session:**

Prompting is not a backend concern anymore. When users need to customize AI behavior, they think in goals, not syntax. The real engineering work is building the translation layer that turns their intuitive controls into structured, type-safe prompts your system can trust.

**Tomorrow: Agentic Backpressure Deep Dive**

Tomorrow we're exploring alternatives to research for improving coding agent results. We'll dig into learning tests and proof-driven development: writing small PoC programs and tests that confirm your understanding of external systems before you get deep into implementation.

Sign up here: https://luma.com/agentic-backpressure-deep-dive

If you have questions, reply to this email or ask on [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
