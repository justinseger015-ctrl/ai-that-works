# Email Generation Command

## Step 1: Determine Target Directory
If this command is invoked with no arguments, ask the user which episode directory to generate an email for.

## Step 2: Read Context
1. List all email.md files: `*/email.md`
2. Read at least 3 recent email.md files to understand the tone, structure, and style
3. Read the README.md from the target episode directory to understand the content

## Step 3: Analyze Email Structure
Emails typically follow this format:
- **Greeting**: "Hello First Name,"
- **Opening**: Reference to "This week's 🦄 ai that works session" with the topic
- **Links**: GitHub repo link and YouTube video link
- **Key Takeaways**: 3-5 numbered or bulleted actionable insights
- **Memorable Quote**: "If you remember one thing from this session:" section
- **Next Session**: Information about the upcoming session with Luma link
- **Call to Action**: Discord link, questions invitation
- **Sign-off**: "Happy coding 🧑‍💻" followed by "Vaibhav & Dex" or similar

## Step 4: Generate Email
Create a follow-up email that:
- Matches the tone of previous emails (casual, technical, actionable)
- Extracts key insights from the README
- Follows the established format
- Includes the 🦄 emoji when referencing "ai that works"
- Uses first-person plural ("we") to describe the session
- Ends with "Happy coding 🧑‍💻"

## Notes
- Keep the tone conversational but informative
- Focus on actionable takeaways readers can apply immediately
- The "If you remember one thing" should be the most important concept
- Links should use the actual GitHub structure: `https://github.com/hellovai/ai-that-works/tree/main/[EPISODE-DIR]`