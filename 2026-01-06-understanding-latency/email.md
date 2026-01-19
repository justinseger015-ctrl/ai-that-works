Hello {firstName},

This week's 🦄 ai that works session explored latency optimization for AI applications.

The full recording is now on [YouTube](https://www.youtube.com/watch?v=wadVIkJnjQE), and all the code is available on [GitHub](https://github.com/hellovai/ai-that-works/tree/main/2026-01-06-understanding-latency).

We covered the performance engineering mindset: find the bottleneck first, then optimize. Most apps can feel 10x faster without changing models.

**Actions you can take today:**

**Fix your caching strategy.** If you're making multiple LLM calls with shared context, DON'T async them all at once. Fire one request first to warm the cache, then parallelize the rest. `async.gather()` is actually slower because none of the requests benefit from caching.

**Audit your prompt tokens.** Look at your largest prompt and remove redundant descriptions in schema fields. If the field name is `file_pattern`, you don't need a description saying "The file pattern to match". Target: cut your prompt tokens by 20% minimum.

**Check your reasoning tokens.** If you're using reasoning models, add `reasoning_effort: "minimal"` to your API calls. Many apps are burning 70% of their latency on invisible reasoning tokens. Only use deep reasoning when you actually need it.

**If you remember one thing from this session:**

Latency optimization is about making your app feel faster, not just run faster. The biggest wins come from prompt token reduction and smart caching, not faster models.

**Tomorrow: Applying 12-Factor Principles to Coding Agent SDKs**

Tomorrow we're going beyond prompts and context engineering. We'll show you how to use agent loops as microservices within deterministic workflows—using the Claude Agent SDK to stitch together micro-agent workflows, accumulating user rules across context windows, and session continuation patterns that actually work in production.

Sign up here: https://luma.com/12-factors-to-coding-agents

If you have questions about this episode, reply to this email or ask on [Discord](https://boundaryml.com/discord). We read everything!

Happy coding 🧑‍💻

Vaibhav & Dex