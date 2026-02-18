"""Core email generation logic."""

from baml_client import b
from baml_client.types import EmailDraft


async def generate_email(
    transcript: str,
    episode_title: str,
    episode_description: str,
) -> EmailDraft:
    """Generate an email draft from episode content.

    Four-stage pipeline:
    1. ExtractEmailStructure - Extract structured bullet points from raw inputs
    2. ComposeEmail - Transform structure into polished email
    3. IdentifyAIPatterns - Identify patterns that make the email sound AI-generated
    4. FixAIPatterns - Rewrite the email fixing those patterns

    Args:
        transcript: Full episode transcript
        episode_title: Title of the episode
        episode_description: Episode description/summary

    Returns:
        EmailDraft with subject, body, and call_to_action
    """
    # Stage 1: Extract structured information
    structure = await b.ExtractEmailStructure(
        transcript=transcript,
        episode_title=episode_title,
        episode_description=episode_description,
    )
    breakpoint()
    # Stage 2: Compose final email
    draft = await b.ComposeEmail(structure=structure)
    breakpoint()

    # Stage 3: Identify AI slop patterns
    patterns = await b.IdentifyAIPatterns(draft=draft)
    breakpoint()

    # Stage 4: Fix the identified patterns
    fixed_draft = await b.FixAIPatterns(draft=draft, patterns=patterns)
    breakpoint()
    return fixed_draft
