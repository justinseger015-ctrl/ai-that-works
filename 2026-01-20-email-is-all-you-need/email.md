Hello {firstName},

This week's 🦄 ai that works session was about building agents that work over email.

The full recording is now on [YouTube](https://www.youtube.com/watch?v=zpfXzk-3Yxw), and all the code is available on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-01-20-email-is-all-you-need).

We did some live testing, walked through the codebase, and broke down the architecture for handling cancellations. For example, when a user sends a follow-up saying "actually no, I have an onsite" five seconds after their first email, the system needs to handle that gracefully. We mapped out how to solve this using queues keyed by thread, separating events from actions, and using locks to stop race conditions.

**Key Takeaways:**

**Email is the universal interface.** 
We often overlook email when designing agents, but it’s where business actually happens. It holds the data, books the meetings, and connects you to customers. The real value here isn't chatting with an LLM; it's delegation. You should be able to forward a vendor email to create a task, or have a customer inquiry automatically update your CRM.

**The bottleneck is data, not AI.** 
Getting clean, usable data from email is harder than the actual modeling. Your current options are mostly SES (which dumps raw blobs into S3) or legacy marketing tools that don't fit the use case. The heavy lifting involves converting messy email threads into a structured, typed format that is actually programmable.

**No UI control means better architecture.** 
Since you can’t control when a user sends a correction or a follow-up, you have to design for interruptions immediately. While many chatbots break when a user changes their mind mid-stream, email forces you to implement queues, state machines, and proper concurrency controls. These constraints ultimately lead to a much more robust system.

**The bottom line:**
Don't view email agents as a replacement for chat. View them as a way to meet users where they are, using the necessary stateful infrastructure to make those agents reliable.

**Next Session: No Vibes Allowed**
Next week we're back to live coding. We'll be adding features to BAML on stream to put these concepts into practice.

Sign up here: https://luma.com/no-vibes-allowed-jan-26

If you have questions, reply to this email or ask on [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex