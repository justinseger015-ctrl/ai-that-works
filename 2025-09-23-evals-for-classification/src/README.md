
# 🦄 large scale classification

> ​llms are great at classification from 5, 10, maybe even 50 categories. but how do we deal with situations when we have over 1000? perhaps its an ever changing list of categories?

[Video](https://youtu.be/6B7MzraQMZk)

[![Large Scale Classification](https://img.youtube.com/vi/6B7MzraQMZk/0.jpg)](https://www.youtube.com/watch?v=6B7MzraQMZk)


## Running this code

```bash
# Install dependencies
uv sync
```

```bash
# Convert BAML files -> Python
uv run baml-cli generate
```

```bash
# Run the code
uv run hello.py
```

## Followup Exercise - Tool Selection from 100s of tools

If you want to play with this code and try to extend it, you can try this exercise.

1. Skim the file at [./tools.json](./tools.json)
2. Load in the list of tools as `Category` or create a similar class for `Tool`
3. Implement `f(tool) -> string` for embedding text and `g(tool) -> string` for LLM text 
4. Update the code to embed and search a user query to select the topk most likely tools
5. Explore some different use inputs for ambiguous tools, see how accurate you can get it

If you want to add more MCP servers or other tools, the code to generate the json is at https://github.com/dexhorthy/thousands-of-tools-mcp

## Followup Exercise - Post-LLM probe

1. Change the core LLM prompt to select out a `Category[]` instead of a single `Category`
2. Add a follow up step (deterministic or LLM-based) to take a list of `Category[]` and select out a final `Category`
3. Write some examples where the final probe can solve closely-overlapping Categories
4. If you did the tool selection exercise, you can use `Tool` instead of `Category` if you prefer


## Diagrams

![image](https://github.com/user-attachments/assets/233eca5d-07a9-4238-a812-bae538dc7b78)

![image](https://github.com/user-attachments/assets/02b775f1-50a2-424f-934a-14982e5025a4)

![image](https://github.com/user-attachments/assets/abe0e587-360f-4d06-8973-cd91a8e4ea0d)

![image](https://github.com/user-attachments/assets/c13795d4-1ada-40a3-9d11-5912dbd3a787)

![image](https://github.com/user-attachments/assets/3dfa6815-c7b0-46cb-b02c-189e51c016c4)

![image](https://github.com/user-attachments/assets/6cb9c541-ba25-478b-8244-62b4114acb97)
