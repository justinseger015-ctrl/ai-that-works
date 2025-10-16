Hello First Name,

We just wrapped two incredible sessions that dive deep into production AI systems—from understanding how they break at scale to building features with AI agents in real-time.

Here's what you missed:

**Anthropic Post Mortem (Oct 7th)** - [Watch](https://youtu.be/bLx-UlRTiEw)

Vaibhav and Aaron (former AWS EC2/Prime Video engineer, current Boundary Co-founder) dissected Anthropic's transparent post-mortem of three critical bugs that hit their production systems in August. We explored the technical depths: how floating-point precision differences between FP16 and FP32 caused wrong token selection, why million-token context windows degraded performance on smaller requests, and how distributed token selection across GPUs can fail in subtle ways.

What we learned:
* Twitter is Anthropic's #1 anomaly detector ("vibe checks" at scale actually work)
* That shiny million-token context window? It was making 30% of Claude Code users' requests worse
* Floating-point math betrays you: `a × b × c ≠ c × b × a` when mixing FP16/FP32 (who knew?)

**No Vibes Allowed: Live Coding with AI Agents (Oct 14th)** - [Watch](https://youtu.be/zNZs19fIDHk)

We took a GitHub issue that had been open since March and implemented comprehensive timeout support for BAML—live on stream. Starting from a 400,000+ line codebase that neither of us had context for, we used the research-plan-implement workflow to ship working code in under 3 hours (what would typically take 1-2 days).

Our live workflow:
* 15 min spec refinement → 30 min AI codebase research → 45 min planning → 90 min implementation
* Result: 3 working phases with passing tests in under 3 hours (vs. 1-2 days traditional)

What actually matters:
* If you're not using voice for talking to coding agents, you're missing out.
* The "magic" prompt that fixes everything? Doesn't exist. Read every line of generated code.
* Stay under 40% context usage or watch your AI turn into a confused junior developer
* That 30-minute research phase? It's the difference between shipping in 3 hours vs. 3 days

PR we opened - https://github.com/BoundaryML/baml/pull/2611

If you remember one thing from these sessions:

Whether you're debugging production AI failures or building with AI agents, the principle is the same: **Less is more**. Use less context for better model performance. Build smaller, testable phases rather than monolithic implementations. Roll back first, investigate later. The best engineering isn't about doing everything at once—it's about doing the right thing at each step.

All code examples, diagrams, and detailed write-ups are available on GitHub:
- Anthropic Post Mortem: https://github.com/ai-that-works/ai-that-works/tree/main/2025-10-07-anthropic-post-mortem
- No Vibes Allowed: https://github.com/ai-that-works/ai-that-works/tree/main/2025-10-14-no-vibes-allowed

**Next Session: Agentic RAG + Context Engineering (Oct 21st)**

RAG vs. Agentic RAG is the hot debate at the forefront of AI Engineering. We'll dive deep on the differences, cut through the buzzword hype with hands-on whiteboarding and live working code. We'll explore the tradeoffs between deterministic retrieval with curated context engineering vs. letting models assemble their own context with tools.

Sign up here: https://lu.ma/febfzi72

If you have any questions about these episodes, reply to this email or ask on Discord. We read everything!

Happy coding 🧑‍💻

Vaibhav & Dex