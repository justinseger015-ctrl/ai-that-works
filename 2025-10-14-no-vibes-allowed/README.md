# 🦄 ai that works: No Vibes Allowed - Live Coding with AI Agents

> A masterclass in AI-assisted software development: Watch as we implement a complex timeout feature for BAML in under 3 hours, demonstrating the research-plan-implement workflow that makes AI coding actually work in production codebases.

[Video](https://www.youtube.com/watch?v=zNZs19fIDHk) (2h3m)

[![No Vibes Allowed](https://img.youtube.com/vi/zNZs19fIDHk/0.jpg)](https://www.youtube.com/watch?v=zNZs19fIDHk)

## Episode Highlights

> "The best engineers have the entire codebase downloaded into their brain. That is still super valuable, the same way it's valuable if you're navigating in an IDE and writing code by hand."

> "A bad line of code is a bad line of code. A bad part of a plan is a hundred bad lines of code."

> "If you're not using voice to prompt for coding tasks, you're just slowing yourself down. When you're typing, you want to think before you type. When you're speaking, you inject more information, which means the model will have better context."

> "The less context you use, the better results you get. We're building our workflow around what I call frequent intentional compaction."

## What We Built

Starting from a GitHub issue that had been open since March, we implemented comprehensive timeout support for BAML, including:
- **Connection timeout** - Time to establish connection
- **Request timeout** - Total end-to-end request time
- **Idle timeout** (streaming only) - Timeout between chunks
- **Time-to-first-token** (streaming only) - Timeout for initial response
- **Total timeout** - Upper bound for composite clients (fallbacks/retries)

## The Workflow

### 1. Specification Phase (15 min)
- Started with existing GitHub issue and rough documentation
- Refined syntax to nest all timeout options under `http` block
- Added critical details (streaming-only timeouts, error handling)
- Used AI to update documentation to match desired user experience

### 2. Research Phase (30 min)
- AI agents explored 400,000+ line codebase
- Identified all relevant files and current timeout implementations
- Found hardcoded timeouts that needed to be made configurable
- Documented testing patterns and code generation pipeline
- Key insight: Found `orchestrator/stream.rs` needed special handling

### 3. Planning Phase (45 min)
- Interactive Q&A to resolve ambiguities (timeout priorities, error handling)
- Broke implementation into 7 phases:
  1. Parsing and validation
  2. Error type definitions
  3. Basic timeout implementation
  4. Streaming timeouts
  5. Composite client timeouts
  6. Integration testing
  7. Runtime configuration
- Each phase independently testable and shippable

### 4. Implementation Phase (90 min)
- Phase 1: Config parsing with validation tests
- Phase 2: Error types for Python/TypeScript SDKs
- Phase 3: HTTP client timeout implementation
- Phase 3B: Python integration tests
- All tests passing by end of session

## Key Takeaways

### On Context Engineering
- **Fresh context windows** for each major phase - don't carry unnecessary history
- **Research documents** serve as compressed context for planning
- **Plan documents** guide implementation without re-reading all code
- **40% context usage** is the sweet spot - restart before hitting limits

### On Working with AI
- **Always read the code** - This isn't magic, you're still responsible
- **Voice > typing** for prompts - Speak freely to provide richer context
- **Opus for research**, Sonnet for implementation
- **Parallel execution** during downtime maximizes productivity

### On Software Engineering
- **Small, testable phases** - Each phase should compile and run
- **Primitive features first** - Get basic clients working before composites
- **Test as you go** - Don't save all testing for the end
- **Architecture matters** - Well-structured codebases are easier for AI to extend

## The Numbers

- **Time invested**: 3 hours (including explanations for stream)
- **Traditional estimate**: 1-2 days for experienced engineer
- **Code touched**: Rust core, Python SDK, TypeScript SDK, 30+ files
- **Tests added**: Parser validation, integration tests, error handling
- **Context restarts**: 3 (staying under 40-60% usage)

## Tools & Techniques Used

- **Claude (Opus)** for codebase research and planning
- **Claude (Sonnet)** for code implementation
- **Specialized agents**: Code locator, pattern finder, analyzer
- **Voice input** via Whisper for faster prompting
- **Obsidian** for readable markdown plans
- **Incremental commits** after each successful phase

## Lessons Learned

1. **Research is 100x leverage** - Spending 30 minutes documenting how the codebase works saves hours of implementation thrashing

2. **Plans are living documents** - Continuously refine based on learnings, but don't obsess over perfection

3. **Phases should mirror how you'd code manually** - If you wouldn't write 500 lines without testing, neither should the AI

4. **Domain expertise still matters** - Having someone who knows the codebase review the plan catches critical issues early

5. **Speed comes from parallelization** - While one agent implements, another can research the next phase

## Resources

- [Session Recording](https://www.youtube.com/watch?v=zNZs19fIDHk)
- [BAML Language](https://github.com/boundaryml/baml)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for next session on [Luma](https://lu.ma/febfzi72)

## Commands & Prompts Used

Available in the [AI That Works repository](https://github.com/ai-that-works/ai-that-works/tree/main/2025-10-14-no-vibes-allowed)

## Whiteboards
