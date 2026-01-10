# 🦄 ai that works: Understanding Latency in AI Applications

> A deep dive into performance engineering for AI applications. We explore all the bottlenecks in agent systems - from prompt caching and token optimization to semantic streaming and UI design. Learn how to make your agents feel faster through strategic latency reduction and smart UX choices.

[Video](https://www.youtube.com/watch?v=wadVIkJnjQE) (1h7m)

[![Understanding Latency in AI Applications](https://img.youtube.com/vi/wadVIkJnjQE/0.jpg)](https://www.youtube.com/watch?v=wadVIkJnjQE)

## Episode Highlights

> "The hardest thing about performance engineering isn't about making code faster - it's about knowing where you want to make your code faster. You have to find the bottleneck first."

> "Latency isn't actually about making your app faster - it's about making your app feel faster. Feelings are a lot more important than the actual latency."

> "Going from a minute down to 30 seconds really doesn't change too much of the workflow for a user. But a minute down to 10 seconds makes a huge difference. It changes the expectation of what the user is going to do."

> "If you're going to parallelize your prompt and you want prompt caching, asking one question first and then asking the others in parallel will give you faster latency than asking all of them together. Fire one, then fire the rest right afterwards."

## Key Takeaways

- **Know Your Bottlenecks**: Before optimizing, identify where latency actually matters in your system. Profile your agent workflows to find the real performance issues.
- **Prompt Caching Strategy**: Design your prompts as append-only arrays. Put static content first, dynamic content last. Use prompt caching effectively by understanding the 1024 token minimum.
- **Semantic Streaming**: Stream meaningful chunks, not individual tokens. Wait for complete ingredients in a recipe, but stream recipe steps as they come. Make your streaming decisions based on what makes semantic sense to the user.
- **Reduce Token Count**: The biggest performance win comes from taking a 4,000 token prompt down to 400 tokens. Remove redundant descriptions, use aliases, and eliminate unnecessary metadata.
- **Reasoning Model Gotchas**: Be aware that reasoning models can generate 70% reasoning tokens that you can't see, dramatically slowing apparent performance. Use minimal reasoning effort when possible.
- **Prefetching**: For idempotent operations, prefetch requests as users type. Block write operations but allow read operations to warm caches before the user hits enter.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=wadVIkJnjQE)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session: [Applying 12-Factor Principles to Coding Agent SDKs](https://luma.com/12-factors-to-coding-agents)

## Whiteboards

<!-- Links to whiteboards will be added manually -->

## Links

<!-- Additional links will be added manually -->