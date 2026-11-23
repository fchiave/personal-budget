# Personal Budget — Product & Technical Roadmap

## MVP (v0.1 – v0.5): Core Local Pipeline
- [x] **v0.1.0 — Ingestion & Tooling Foundation:**
  - Typed Capital One CSV parser (`Transaction` frozen dataclass + `Decimal` currency math).
  - Dev Container with `uv`, `pytest`, `ruff`, `Makefile` quality gates, and GitHub Actions CI.
- [ ] **v0.2.0 — SQLite Ledger & Deduplication (`feat/sqlite-ledger`):**
  - Local SQLite storage (`data/ledger.db`) using integer cents (`amount_cents`).
  - Deterministic `transaction_id` hashing with per-file occurrence counters for same-day identical charges.
  - Status lifecycle (`pending` -> `categorized` | `needs_review` -> `verified`) to protect manual overrides.
- [ ] **v0.3.0 — Merchant Normalization & Local LLM Categorization:**
  - Strip store numbers/POS prefixes (`#0330`, `TST*`, `SQ *`) and check SQLite merchant history cache first.
  - Route unseen merchants to local `qwen3:14b` (Ollama) using a strict category `Enum`.
  - Flag ambiguous big-box merchants (Target, Amazon, Walmart) as `needs_review`.
- [ ] **v0.4.0 — Interactive Review Queue:**
  - Lightweight CLI (or local Marimo/Streamlit view) to review and tag `needs_review` transactions as `verified`.
- [ ] **v0.5.0 — Monthly Spending Summary (Polars):**
  - Convert categorized ledger rows to Polars DataFrames.
  - Generate month-over-month category totals (excluding internal credit card payments/transfers).

---

## Post-MVP Feature Ideas (v1.0+)

### Analytics & Behavioral Insights
- **Recurring Bills & Price-Creep Alerts:** Detect recurring subscriptions by `(clean_merchant, amount)` and flag silent price increases against historical medians.
- **Monthly Burn-Rate Pacing:** Track cumulative day-of-month spend against historical monthly averages (weekday vs. weekend weighted) to project end-of-month totals.
- **Seasonal Baselines & Outlier Detection:** Compare spending against same-month prior years and flag statistical category outliers.

### Local AI & Interactive Tooling
- **Natural-Language Financial Analyst (`qwen3:14b`):** Give the local LLM read-only access to pre-approved Polars summary queries to answer ad-hoc spending questions privately.
- **Local Web Dashboard:** Interactive browser dashboard (Marimo or Streamlit on `localhost`) for filtering categories, inspecting trends, and clearing the `needs_review` queue.

### Multi-Account Expansion
- **Checking Account & Transfer Matching:** Ingest checking account CSVs and automatically pair outgoing ACH payments with credit card autopay credits within a ±3-day window for true net cash-flow tracking.
