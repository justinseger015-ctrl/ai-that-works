// Structured types for parsing design discussion output

class DesignOutput {
    summary string @description("Summary of what we understand so far")
    openDesignQuestions string[] @description("Questions that still need answers")
}

// Parse unstructured design discussion into structured output
function ParseDesignDiscussion(raw_text: string) -> DesignOutput {
    client Claude
    prompt #"
        Parse the following design discussion into structured JSON.
        Extract a summary of decisions made and any open questions.

        Text:
        ---
        {{ raw_text }}
        ---

        {{ ctx.output_format }}
    "#
}
