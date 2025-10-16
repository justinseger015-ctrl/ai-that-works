# 🦄 ai that works: Anthropic Post Mortem

> Deep technical analysis of Anthropic's August 2024 incidents, exploring how floating-point precision, context window routing, and distributed token selection can break production AI systems at scale.

[Video](https://youtu.be/bLx-UlRTiEw) (1h)

[![Anthropic Post Mortem](https://img.youtube.com/vi/bLx-UlRTiEw/0.jpg)](https://youtu.be/bLx-UlRTiEw)

## Episode Summary

Vaibhav Gupta and Aaron (co-founder, former AWS EC2/Prime Video engineer) dissect Anthropic's detailed post-mortem of three critical bugs that affected their production systems. They explore the technical intricacies of how models select tokens across distributed GPUs, why longer context windows can degrade performance, and how compiler optimizations mixing 16-bit and 32-bit floating-point math led to incorrect token selection. The discussion extends to practical lessons for AI engineers: building observability into AI systems, using "vibe checks" from social media for anomaly detection, and the critical importance of rollback strategies. They also analyze OpenAI's new Agent Builder and the broader trend of visual workflow tools for non-technical users.

## Key Technical Deep Dives

### Context Window Routing Bug
- **Impact**: 30% of Claude Code users affected
- **Root Cause**: Million-token context windows degraded performance on smaller requests
- **Lesson**: Less context often yields better results - models trained on different context lengths perform differently when information needs to bridge across tokens
- **Technical Detail**: RoPE (Rotary Position Embedding) scaling changes how models perceive token positions when expanding context

### Floating Point Precision Bug
- **Impact**: 0.8% of traffic affected, but critical for temperature=0 use cases
- **Root Cause**: TPU compiler randomly optimized some operations to FP32 instead of FP16
- **Issue**: In floating point math, `a × b × c ≠ c × b × a`, and FP16 vs FP32 results differ
- **Result**: Wrong tokens selected when comparing probabilities near boundaries (e.g., 0.509 vs 0.501)

### Distributed Token Selection
- **Architecture**: 2M token vocabulary split across multiple GPUs (32K tokens each)
- **Process**: Each GPU proposes top candidates, central node picks global maximum
- **Bug**: Local candidate selection failed due to floating point comparison issues
- **Effect**: Global top token missing from candidate array

## Key Engineering Takeaways

> "Don't be a hero, roll back" - AWS's golden rule that saved countless production incidents

> "Use less context. I promise you, your pipelines will be more accurate."

> "The minute I realize I need specific folder names... I'm basically writing code in a UI builder"

### On Observability & Debugging
- Anthropic monitors Twitter sentiment as their primary anomaly detection - "vibe checks" work at scale
- Build product metrics tied to AI quality (chat thread length, user retention)
- Need new observability tools for subtle AI failures vs traditional 500 errors
- Phoenix, Arizona breaks many systems due to heat affecting camera calibration - you need diverse eval data

### On Deployment & Testing
- Deploy slowly - never push worldwide simultaneously
- Use feature flags for instant rollbacks (Vercel one-click rollback mentioned)
- If rollback doesn't fix it, it's likely a model/infrastructure issue
- Collect production data continuously and turn subsets into eval datasets
- 30 test cases is often the magic number for basic coverage

### On Hallucinations vs Failures
- "Hallucination" is poorly defined - often just means "disagrees with me"
- Infrastructure failures: Model picks wrong token due to bugs
- Hallucinations: Model generates plausible but incorrect content
- Detection strategy: Calculate checksums, validate structured outputs programmatically

## Agent Builders & The Future

### OpenAI's Agent Builder
- Built in 6 weeks using Codex
- Target audience: Non-technical users afraid of code
- Key value: Integrations (Google Docs, Drive, etc.)
- Problem: Complex schemas become unmanageable in visual builders
- Missing feature: How do you create reusable functions/components?

### The Moat Question
- Model inference is becoming commoditized
- Real value: How AI composes with your existing stack
- Platform lock-in via proprietary APIs (Realtime API, model-specific tools)
- Parallel to AWS: Once you're in, switching cost is prohibitive

## Practical Advice for Builders

1. **Context Engineering**: Treat RAG, memory, and prompts as unified context optimization
2. **Rollback First**: When issues arise, rollback immediately, investigate later
3. **Social Signals**: Monitor Twitter/forums for "vibe checks" on model quality
4. **Test Distribution**: Your evals must span your actual user behavior distribution
5. **Prompt Swapping**: If Anthropic fails, try OpenAI, then prompt engineering
6. **Feature Flags**: Essential for AI systems where failures are subtle

## Resources

- [Anthropic's Post-Mortem Article](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues)
- [Session Recording](https://youtu.be/bLx-UlRTiEw)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for next session: [Live Coding with Claude + Codelayer](https://lu.ma/baml)

## Episode Chapters

- 00:00 - Introduction and Technical Difficulties
- 02:12 - Anthropic's Recent Downtime Overview
- 07:58 - Context Window Routing Issues Explained
- 10:02 - How Transformers Move Information Between Tokens
- 14:28 - Output Corruption & Performance Optimization Bugs
- 19:42 - Floating Point Precision & Token Selection Deep Dive
- 25:07 - Distributed GPU Token Probability Calculation
- 31:42 - Debugging Strategies & AWS Lessons
- 35:18 - Deployment Best Practices for Startups
- 39:01 - Failures vs. Hallucinations Definition
- 43:28 - Building Effective Eval Pipelines
- 44:18 - OpenAI's Agent Builder Analysis
- 49:30 - The Future of AI Integrations & Platform Lock-in
- 54:03 - Research-Plan-Implement Workflow Discussion

## Whiteboards

## Links