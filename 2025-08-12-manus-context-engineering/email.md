Hello First Name,

This week's 🦄 ai that works session was on "Decoding Context Engineering Lessons from Manus"!

The full recording is now on YouTube, and the whiteboards from the session are available on GitHub:
* YouTube: https://youtu.be/OaUOHEHtlOU
* GitHub: https://github.com/hellovai/ai-that-works/tree/main/2025-08-12-manus-context-engineering

We covered a lot on context engineering and how to optimize LLMs for better performance. Here's a super quick recap:

Optimize Your Cache, Optimize Your Performance: Your prompt's structure directly impacts speed and cost. By keeping your system message consistent and placing dynamic variables (like the user's question) at the end of the input, you can intelligently utilize the KV cache, leading to significant performance gains.

Reinforce Context, Don't Just Assume: In long interactions, an LLM can lose track of the original goal. Instead of relying on its memory, periodically re-inject relevant information or tasks to reinforce the context. Also, be judicious with few-shot prompting—use it only when needed and structure examples properly to avoid biasing the output.

If you remember one thing from this session:
Context Engineering is an active process. It's about managing the model's memory with smart cache strategies, structuring inputs for efficiency, and reinforcing key information to guide the LLM, ensuring it stays on-task and performs effectively.

We also had a fascinating session the week prior about "Advanced Context Engineering for Coding Agents", video/whiteboards/code are on the Github at https://hlyr.dev/he-gh

Our next session on August 19th will be all about "Interruptible Agents". Anyone can build a chatbot, but the user experience is what truly sets it apart. Can you cancel a message? Can you queue commands while it's busy? How finely can you steer the agent? We'll explore these questions and code a solution together.
Sign up here: https://lu.ma/6rf28j8w

If you have any questions, reply to this email or ask on Discord: https://www.boundaryml.com/discord. We read every message! Happy coding 🧑‍💻

Vaibhav & Dex