"""Ingestion and validation for Capital One CSV transaction exports."""

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

# Not needed now, uncomment when using Polars to do large data analysis
# import polars as pl

__all__ = ["Transaction", "load_capital_one_csv"]

# Expected CSV header names — column order does not matter
REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {
        "Transaction Date",
        "Posted Date",
        "Card No.",
        "Description",
        "Category",
        "Debit",
        "Credit",
    }
)


@dataclass(frozen=True, slots=True)
class Transaction:
    """Normalized, immutable financial transaction record."""

    transaction_date: date
    posted_date: date
    card_no: str
    description: str
    category: str
    amount: Decimal


def _parse_amount(debit_raw: str | None, credit_raw: str | None) -> Decimal:
    """Convert raw Debit and Credit strings into a single signed Decimal amount.

    Debits are represented as negative values and credits as positive values.
    Raises ValueError if both fields are empty or whitespace-only.
    """
    debit_str = (debit_raw or "").strip()
    credit_str = (credit_raw or "").strip()

    if not debit_str and not credit_str:
        raise ValueError("Both Debit and Credit are empty")

    debit = Decimal(debit_str or "0")
    credit = Decimal(credit_str or "0")
    return credit - debit


def load_capital_one_csv(path: Path) -> list[Transaction]:
    """Load and validate a Capital One CSV export into Transaction models."""
    transactions: list[Transaction] = []

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        # Validate columns
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        for line_num, row in enumerate(reader, start=2):
            try:
                transactions.append(
                    Transaction(
                        transaction_date=date.fromisoformat(
                            (row["Transaction Date"] or "").strip()
                        ),
                        posted_date=date.fromisoformat((row["Posted Date"] or "").strip()),
                        card_no=(row["Card No."] or "").strip(),
                        description=(row["Description"] or "").strip(),
                        category=(row["Category"] or "").strip(),
                        amount=_parse_amount(row["Debit"], row["Credit"]),
                    )
                )
            except (ValueError, InvalidOperation) as exc:
                raise ValueError(f"Line {line_num}: {exc}") from exc

    return transactions
