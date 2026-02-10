Hello {firstName},

This week's 🦄 ai that works session explored using agent loops as building blocks inside deterministic workflows—not as the whole system.

The full recording is now on [YouTube](https://www.youtube.com/watch?v=qgAny0sEdIk), and all the code is available on [GitHub](https://github.com/hellovai/ai-that-works/tree/main/2026-01-13-applying-12-factor-principles-to-coding-agent-sdks).

We covered the trade-off between variance and consistency in agentic systems, how to use structured outputs to enforce workflow phases, and why compounding error rates mean you need to be intentional about context window size. We also had Mike Hostetler on to show how his team of 25 engineers is using structured Ralph Wiggum workflows to learn agentic coding.

**Actions you can take today:**

**Stop using prompts for control flow.** If you're writing "IMPORTANT: do step 2 before step 3" in all caps, that belongs in code. Break your workflow into separate phases, each with its own prompt and structured output schema. The model can't skip a phase when your code enforces the exit condition.

**Pick your lever: accuracy or context size.** Even 99% accuracy per step compounds to ~80% success over 20 steps. You can either make each step more accurate (better prompts, evals, judges) or shrink your context window with intentional compaction between phases. Those are the only two options.

**Use structured outputs as your state machine.** Define a schema for each phase. The model outputs JSON with the fields you need to make routing decisions in code. No prompt engineering required—just if statements.

**If you remember one thing from this session:**

Don't use prompts for control flow; use control flow for control flow. The more you enforce workflow transitions with structured outputs and exit conditions, the more consistent your results get—without losing the flexibility agents provide.

**Tomorrow: Email is All You Need**

Tomorrow we're exploring what happens when your coding agent communicates via email instead of chat. We'll dig into async workflows, context management across long-running tasks, and the constraints that email APIs impose on agent architecture.

Sign up here: https://luma.com/email-is-all-you-need

If you have questions about this episode, reply to this email or ask on [Discord](https://boundaryml.com/discord). We read everything!

Happy coding 🧑‍💻

Vaibhav & Dex
