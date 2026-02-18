# Clip Extractor

Extract high-impact social media clips from AI That Works episode transcripts using AI-powered analysis.

## Overview

The `clip_extractor` module uses a two-stage AI pipeline to identify the most impactful moments from episode transcripts. It analyzes the full transcript to extract key takeaways, then identifies specific clips that would work well for social media or promotional use.

## Architecture

### Two-Stage Pipeline

1. **Stage 1: Extract Key Takeaways** (`ExtractEmailStructure`)
   - Analyzes the full transcript and episode metadata
   - Extracts 2-3 key bullet points summarizing main concepts
   - Identifies the single most important takeaway
   - Provides context for what makes a clip "impactful"

2. **Stage 2: Find High-Impact Clips** (`ExtractHighImpactClips`)
   - Uses the key takeaways as guidance
   - Searches the transcript for moments that:
     - Contain surprising insights or counterintuitive advice
     - Explain complex concepts in simple, memorable ways
     - Feature "aha moments" or breakthrough realizations
     - Are self-contained and understandable without context
     - Are concise (less than 60 seconds when spoken, ~120-180 words)
   - Returns exactly 3 clips, ranked from most to least impactful

### Output Structure

Each extracted clip includes:

- **rationale**: Why this clip is high-impact and how it relates to key themes
- **start_timestamp**: When the clip begins (e.g., "33:46")
- **end_timestamp**: When the clip ends (e.g., "35:15")
- **speaker**: The primary speaker in this clip
- **transcript_excerpt**: The exact text from the transcript, including speaker names and timestamps
- **hook**: A punchy 1-2 sentence summary for use as a caption or title

## Usage

### Command Line Interface

```bash
python -m src.clip_extractor.cli \
  --transcript transcript.txt \
  --title "Episode Title" \
  --description "Episode description or summary" \
  --output ./output/directory
```

### Arguments

- `--transcript`, `-t`: Path to the transcript file (required)
- `--title`: Episode title (required)
- `--description`, `-d`: Episode description or summary (required)
- `--output`, `-o`: Output directory where `clips.json` will be written (required)

### Example

```bash
python -m src.clip_extractor.cli \
  --transcript 2026-02-10-agentic-backpressure/transcript.txt \
  --title "Agentic Backpressure Deep Dive" \
  --description "Understanding how to manage agent workloads and prevent system overload" \
  --output 2026-02-10-agentic-backpressure
```

This will create `2026-02-10-agentic-backpressure/clips.json` with the extracted clips.

## Output Format

The `clips.json` file contains an array of clip objects:

```json
[
  {
    "rationale": "This clip explains a counterintuitive concept about...",
    "start_timestamp": "33:46",
    "end_timestamp": "35:15",
    "speaker": "Dex",
    "transcript_excerpt": "Dex (33:46.123)\nThe key insight here is...",
    "hook": "Why traditional load balancing fails with AI agents"
  },
  ...
]
```

## Requirements

- Python 3.10+
- BAML (for structured LLM outputs)
- Environment variables:
  - API keys for the configured LLM client (typically set in `.env` at project root)
- Dependencies:
  - `baml_client` (generated from BAML configuration)
  - `python-dotenv`

## Implementation Details

### BAML Functions Used

- `ExtractEmailStructure` (from `email.baml`): Extracts key takeaways
- `ExtractHighImpactClips` (from `clip.baml`): Finds specific clips

### Type Definitions

The `HighImpactClip` type is defined in `baml_src/clip.baml` and provides structured output from the LLM, ensuring consistent formatting and all required fields are present.

### Async Processing

The module uses Python's `asyncio` for efficient async processing of LLM calls, allowing the pipeline stages to be parallelized when possible.

## Next Steps

After extracting clips, you can:
1. Review the clips in `clips.json`
2. Use the timestamps to extract video segments
3. Use the hooks as social media captions
4. Adjust the rationale to understand why each clip was selected
