# Building a Prompt Optimizer

> What happens when models can write really good prompts? Exploring JEPA, genetic algorithms, and building your own prompt optimizer.

[Video](https://www.youtube.com/watch?v=IkSEXg6f4KY)

[![Building a Prompt Optimizer](https://img.youtube.com/vi/IkSEXg6f4KY/0.jpg)](https://www.youtube.com/watch?v=IkSEXg6f4KY)

## Overview

A deep dive into prompt optimization with special guest Greg from the BAML team. We explore:

- **What is JEPA?** - Genetic Pareto algorithm for prompt optimization
- **How it works** - LLM-driven exploration vs traditional gradient descent (GRPO)
- **The Pareto frontier** - Optimizing across multiple dimensions (accuracy, tokens, latency)
- **Genetic algorithms** - How prompts "meet and make babies" to explore the search space
- **Live demo** - Building and running a prompt optimizer with BAML

## Key Concepts

- **JEPA vs GRPO**: JEPA uses LLMs to suggest better prompts instead of fine-tuning with gradients - "the bitter lesson for prompt optimization"
- **Pareto optimization**: Finding prompts that are optimal across multiple competing metrics
- **Avoiding overfitting**: When optimizing shared components (system prompts, data models), you need to optimize across all prompts that use them
- **Constrained editing**: Like Claude Code's Notebook Edit tool, prompt optimizers need constrained ways to edit specific parts of prompts

## Links

- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

