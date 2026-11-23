# Personal Budget 

## Idea
Creating a local budget visualizer. Powered by Python and LLMs. 

Input - Monthly spending CSVs from Capital One

Output - Properly formatted spending summary month by month

## Checkpoints

0. CSVs with transaction info in and setup project infrastructure
1. Python parses input
**We are here**
2. Store & deduplicate transactions in SQLite
3. LLM cleans fuzzy input
4. LLM categorizes transactions
5. Python verifies LLM work
6. Python visualizes

### 0. CSVs with transaction info in

Downloaded manually from Capital One portal per statement. See: "budget/data"

---

### 0. Setup Project Infrastructure

At this stage, I have prepped contents for checkpoint 1 work.
I localized qwen3:14b and am using that - thinking mode is good, still get good results without it.
Still need to think big picture and prep folder/file architecture.
Then set up the logistics - I want code in this project containerized. 

Container 2 (Dev Container) is built from a Dockerfile and requirements.txt (Python/SQL libraries) in this repo, bridged into Zed via .devcontainer/devcontainer.json with host networking so your code, terminal, and AI agent execute inside Docker while .gitignore excludes local datasets, caches, and .env secrets from Git.

```
budget/
├── data/
│   └── capital_one.csv
├── src/
│   ├── clean_input.py
│   ├── categorize.py
│   └── visualize.py
├── Dockerfile
├── requirements.txt
└── .devcontainer/
    └── devcontainer.json
```

I ran `docker exec -it ollama-global bash` to jump into my LLM container and then `ollama pull qwen3:14b` to download qwen3.
I can remove any model by running `ollama rm <model-name>` in the LLM container.

Need to refresh Zed to make sure it picks up the model after adding, click into AI window on left, press Ctrl+Alt+C, "LLM Providers" -> Configure, scroll down to "Ollama" -> Configure, click refresh where it says "Connected" on bottom right.

---

### [Superseded by [Dev Container Infrastructure](#dev-container-infrastructure)] Development Infrastructure

Working now to setup the infrastructure for development - Docker dev container and hooking up into Zed.
Going to start by building a slim python docker container with a Dockerfile.
Then will connect it to Zed.

Holy moly, difficult.
Took a bit to get set up properly.
Now using a docker-compose.yml file to coordinate the docker stuff, lays foundation for future database/frontend container connections. 
Building through Zed creates a custom image off of the defined `budget-app` image tag and creates an app-dev container called `budget-app-dev`.
When any changes are made to the Dockerfile, you must clear out the container and image so it can be rebuilt properly:

`docker stop budget-app-dev
docker rm budget-app-dev
docker rmi budget-<hashID>-features:latest`

When using Zed, the container will live even after closing the IDE.
The container will start on PC reboot as well.
Zed will save recent projects, open by clicking on the project name in the top left or File > Open Remote > Connect Dev Container.

If needed, you can manually start the container from the .devcontainer info with Ctrl+Shift+P to open the Command Pallete and run "Open dev container". 

----

### Git Integration

Next step should be to get a git repo going. 

Set up SSH auth to git account on local at ~/.ssh and with ~/.gitconfig.
Looking to passthrough SSH_AUTH_SOCK (ssh agent) to the container to handle authentications.
Currently doing through docker-compose.override.yml.

Agent passthrough success, docker container recreated properly.
Git is authenticating properly to github.com.
Noticing now that the Docker container runs with the `root` user.
This can cause file permission errors on the bind mount.
Cleaner to give Docker its own user.
Dev container now set up with its own user `devuser`.
Git auth passthrough working as expected.
Ready to git init in container.

Git repo created at `https://github.com/fchiave/personal-budget`. 

---

### Dev Container Infrastructure

Running into container issues on start up.
Now manually managing container state instead, this cleans up the containerization approach as a whole.

Makefile created to simplify commands as container names vary per build.
Container state now handled through `make` commands: `make up`, `make down`, `make status`, `make clean`.
Stop container when done working with `make down`, start existing container to begin work with `make up`, check container status with `make status`.

When fundamental container changes are made, a new image and container need to be built.
Tear down with `make clean` and use Zed's Command Palette (Ctrl+Shift+P) to run "projects: open dev container". 

---

### 1. Python parses input

Worked on this today.
Initially, I was going to use Pandas but kept running into typing warnings with indexing.
I want to keep things clean so I decided to transition over into a thinner, core python solution: dataclasses.

Data is read in from csvs and each entry is converted to a `Transaction`, seen below.
```python
@dataclass(frozen=True, slots=True)
class Transaction:
    """Normalized, immutable financial transaction record."""

    transaction_date: date
    posted_date: date
    card_no: str
    description: str
    category: str
    amount: Decimal
```
Currently, the data is ingested and creates a `list[Transactions]` to be used in the data pipeline.
In the future, I will have a database that stores these transactions.
This way, I will separate my pipeline, having a flow to ingest data into the database, handling distinct transactions and protecting my history, and a different pipeline to inspect/report the data.

For future reporting and dashboards, I plan to convert `Transaction` records into ***Polars*** Dataframes, that code is saved here for later reference.
```python
# Add import to top of file
from collections.abc import Sequence


def to_dataframe(transactions: Sequence[Transaction]) -> pl.DataFrame:
    """Convert validated transactions into a Polars DataFrame for reporting."""
    return pl.DataFrame(
        transactions,
        schema={
            "transaction_date": pl.Date,
            "posted_date": pl.Date,
            "card_no": pl.String,
            "description": pl.String,
            "category": pl.String,
            "amount": pl.Decimal(scale=2),
        },
    )
```
I removed pandas from the container as well with this change.

---

### Dev Container Build Management

Looking to swap dependency management from `pip` + `requirements.txt` over to `uv` and `pyproject.toml`.
This allows for separation of dependencies between runtime (currently none) and dev tooling (testing, linting).

Dependencies swapped in, container is now built using `uv`, dependencies are handled in a virtual environment stored in `devuser`.
Dependencies are defined in pyproject.toml.

Linting and testing shortcuts are defined in Makefile now.
Run `make test` to run pytest test suite in the dev container.
Run `make lint` to check linting without modifying files.
Run `make format` to auto-fix lint issues and format code.
Run `make check` before committing to run full quality gate (runs lint and test).

CI/CD implemented using GitHub Actions, defined in `.github/workflows/ci.yml`.
The "CI" workflow pulls the latest project code, sets up uv, and runs the linter and testing suite.
This workflow runs on every PR/push to main/dev.

---

### Git Workflow

1. **Branch off `dev`:** Create a new branch prefixed with `feat/` (new functionality) or `chore/` (tooling, dependencies, maintenance) from an up-to-date `dev` branch (`git checkout -b feat/<name>`).
2. **Develop & verify locally:** Build the feature and run `make check` inside the container to verify `ruff` linting/formatting and `pytest` pass.
3. **Open a PR into `dev`:** Push the branch and open a Pull Request targeting `dev`. GitHub Actions will automatically run the CI check suite (`uv sync --locked`, `ruff`, and `pytest`).
4. **Squash and merge:** Once CI is green, squash and merge the PR into `dev` on GitHub.
5. **Clean up locally:** Run `make sync` to switch back to `dev`, pull the squashed commit, prune stale remote branches, and delete the merged local branch.

---

### 2. Store & deduplicate transactions in SQLite

Decided on **SQLite** (`data/ledger.db`) over a separate PostgreSQL Docker service.
Since this is a single-user local tool, SQLite solves all my actual needs without extra container complexity and keeps financial data private. 
As the code is service-agnostic, I can hook in a PosgreSQL Docker service in the future if needed.

Key design notes for database implementation (`feat/sqlite-ledger`):
- **Same-day deduplication:** Compute a SHA-256 `fingerprint` from raw bank fields plus a per-file occurrence counter so identical same-day purchases (e.g., two coffees at the same spot) are both preserved, while re-importing overlapping monthly statements is safely skipped via `INSERT OR IGNORE`.
- **Exact currency storage:** Store `amount_cents` as `INTEGER` (`int(amount * 100)`) instead of `REAL` to prevent floating-point rounding drift.
- **LLM-ready schema:** Keep raw bank fields (`raw_description`, `bank_category`) alongside nullable enrichment columns (`clean_merchant`, `clean_category`, `status`) so `qwen3:14b` only processes newly inserted rows and can be re-run safely if prompts change.
