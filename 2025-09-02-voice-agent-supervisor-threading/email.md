Hello First Name,

This week's 🦄 ai that works session was all about building "Voice Agents and Supervisor Threading"! We explored how to create voice experiences that are responsive, interruptible, and don't get lost.





The full recording, code, and diagrams from the session are now available on GitHub:
https://github.com/ai-that-works/ai-that-works/tree/main/2025-09-02-voice-agent-supervisor-threading

https://youtu.be/UCqD_KUyUJA



We covered a lot on what makes voice agents truly work. Here’s a super quick recap:

Voice agents aren't just chatbots with a microphone. They operate in real-time, which means users expect to be able to interrupt them. A simple request-response loop often falls short.

A powerful pattern we explored is thinking in threads. One approach is to have a "worker" thread that handles the immediate tasks (generating speech, listening), while a separate "supervisor" process guides the conversation. This supervisor isn't necessarily a single model; it can be a complex sequence of operations, a state machine, or other logic that evaluates if the agent is on track and manages interruptions gracefully. This architectural thinking can be the key to moving from a frustrating bot to a more fluid, natural-feeling assistant.

If you remember one thing from this session:
A great voice agent is often a system of interacting processes, not just one LLM call in a loop. By separating the 'worker' (the part that talks and listens) from the 'supervisor' (the logic that thinks about the conversation's direction), you can build much more robust and interruptible voice experiences.

This session builds directly on our previous one about "Interruptible Agents" #19! (https://boundaryml.com/podcast/2025-08-19-interruptible-agents)

Our next session will be on Tuesday Sept 9 about "Generative UIs and Structured Streaming". Sign up here: https://luma.com/2g1xfjts

If you have any questions, reply to this email or ask on Discord: https://www.boundaryml.com/discord



We read every message! Happy coding 🧑‍💻

Vaibhav & Dex

