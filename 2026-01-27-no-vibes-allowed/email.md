Hello {firstName},

This week's 🦄 ai that works session was a live coding throwback where we built real features in BAML on stream.

The full recording is now on [YouTube](https://www.youtube.com/watch?v=Xq8VxnGVStg), and all the code is available on [GitHub](https://github.com/hellovai/ai-that-works/tree/main/2026-01-27-no-vibes-allowed).

We tackled adding a WebAssembly syscall bridge to BAML's execution engine (Bex). The goal: let the BAML playground pass JavaScript callbacks down into Rust, so things like file systems and network calls can be virtualized in the browser. We coded it live using a structured RPI workflow, walking through how we ship complex systems without traditional code reviews.

**Actions you can take today:**

**Generate architecture diagrams automatically.** We showed our `cargo stow` tool that reads your crate dependencies and outputs an SVG diagram. When an LLM adds a bad dependency, CI fails. The diagram also makes it obvious when something is misnamed or when boundaries are violated. You can build something similar for your stack using existing dependency analysis tools plus a layout engine like GraphViz.

**Split "research" from "design" in your agentic workflows.** We used a two-phase approach: first generate objective research questions about the codebase (without telling the model what we're building), then feed those questions to a fresh context window. This keeps the research factual instead of biased toward a particular implementation.

**Use control flow for control flow.** We referenced our earlier episode on 12-factor agent principles. If you're writing "IMPORTANT: do step 2 before step 3" in your prompts, that belongs in code. Break workflows into phases with structured outputs as exit conditions.

**If you remember one thing from this session:**

The teams shipping complex AI-assisted code at high velocity aren't skipping code reviews because they're reckless. They're replacing reviews with automated architecture enforcement (dependency rules, generated diagrams, CI checks) and structured agentic workflows that force clarity at each step.

**Tomorrow: Prompting is Becoming a Product Surface**

Tomorrow we're exploring how prompts are shifting from developer tooling to user-facing features. We'll dig into why more products are exposing prompt customization directly to end users, and what that means for how you build AI-powered applications.

Sign up here: https://lu.ma/baml

If you have questions about this episode, reply to this email or ask on [Discord](https://boundaryml.com/discord). We read everything!

Happy coding 🧑‍💻

Vaibhav & Dex
