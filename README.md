# Personal Budget

Local budget visualizer powered by Python and local LLMs (`qwen3:14b` via Ollama).

- **Input:** Monthly spending CSVs from Capital One (`data/`)
- **Output:** Properly formatted spending summary month by month

## Pipeline
0. CSVs with transaction info in and project infrastructure setup *(Done)*
1. Python parses input into validated `Transaction` records *(Done)*
2. Store & deduplicate transactions in SQLite *(Next)*
3. LLM cleans fuzzy merchant descriptions
4. LLM categorizes transactions
5. Python verifies LLM work
6. Python visualizes monthly summaries (via Polars)

## Quick Commands (`Makefile`)
- `make up` / `make down` — Start or stop the Dev Container
- `make check` — Run Ruff linting/formatting checks and `pytest` inside the container
- `make format` — Auto-fix lint issues and format code with Ruff
- `make sync` — Run after finishing a feature/chore branch. Switch to `dev`, pull latest changes, prune remotes, and delete merged local branches
- `make clean` — Tear down container and images before rebuilding in Zed

## Project Structure
```text
├── .github/workflows/ci.yml   # GitHub Actions CI (uv + ruff + pytest)
├── .devcontainer/             # Docker Compose & Dev Container config
├── docs/work.md               # Chronological build log & architecture notes
├── src/clean_input.py         # Capital One CSV ingestion & Transaction model
├── tests/                     # pytest unit test suite
├── AGENTS.md                  # Coding standards & data boundary rules
├── Makefile                   # Container, testing, and Git workflow shortcuts
└── pyproject.toml             # uv dependencies, pytest, and Ruff config
```

## Notes & Setup
See [docs/work.md](./docs/work.md) for detailed build logs, Ollama setup, and Git workflow notes.
