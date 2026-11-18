# Personal Budget

Local budget visualizer powered by Python and local LLMs (`qwen3:14b` via Ollama).

- **Input:** Monthly spending CSVs from Capital One (`data/`)
- **Output:** Properly formatted spending summary month by month

## Pipeline
0. CSVs with transaction info in and project infrastructure setup *(Done)*
1. Python parses input
2. LLM cleans fuzzy input
3. LLM categorizes transactions
4. Python verifies LLM work
5. Python visualizes

## Notes & Setup
See [work.md](./docs/work.md) for dev container commands, Ollama setup, and build notes.
