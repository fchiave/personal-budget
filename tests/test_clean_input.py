from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.clean_input import Transaction, load_capital_one_csv

# ---------------------------------------------------------------------------
# Helper to write sample CSV
# ---------------------------------------------------------------------------


def write_sample_csv(tmp_path: Path, content: str) -> Path:
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(content, encoding="utf-8-sig")
    return csv_path


SAMPLE_CSV = """Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
2026-11-07,2026-11-09,9130,HARRIS TEETER #0330,Merchandise,23.42,
2026-11-05,2026-11-06,9130,NYC HALAL BITES,Dining,34.60,
2026-11-04,2026-11-06,9130,CHICK-FIL-A  #00699,Dining,2.91,
2026-11-05,2026-11-05,9130,CAPITAL ONE AUTOPAY PYMT,Payment/Credit,,1210.73
2026-11-04,2026-11-05,9130,MCDONALD'S F33850,Dining,14.81,
2026-11-04,2026-11-05,9130,HARRIS TEETER #0112,Merchandise,20.07,
2026-11-03,2026-11-04,9130,BOJANGLES 53,Dining,18.07,
2026-11-04,2026-11-04,9130,TST*ALBARAKA RESTAURA,Dining,56.75,
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_load_capital_one_csv_basic(tmp_path: Path) -> None:
    csv_path = write_sample_csv(tmp_path, SAMPLE_CSV)
    transactions = load_capital_one_csv(csv_path)

    assert len(transactions) == 8

    # Verify first debit transaction structure and types
    assert transactions[0] == Transaction(
        transaction_date=date(2026, 11, 7),
        posted_date=date(2026, 11, 9),
        card_no="9130",
        description="HARRIS TEETER #0330",
        category="Merchandise",
        amount=Decimal("-23.42"),
    )

    # Verify exact signed amounts across all rows (debits negative, credits positive)
    expected_amounts = [
        Decimal("-23.42"),
        Decimal("-34.60"),
        Decimal("-2.91"),
        Decimal("1210.73"),
        Decimal("-14.81"),
        Decimal("-20.07"),
        Decimal("-18.07"),
        Decimal("-56.75"),
    ]
    assert [t.amount for t in transactions] == expected_amounts


def test_missing_required_columns(tmp_path: Path) -> None:
    csv_path = write_sample_csv(
        tmp_path,
        "Transaction Date,Posted Date,Card No.,Description,Category,Debit\n",
    )

    with pytest.raises(ValueError, match=r"Missing required columns: \['Credit'\]"):
        load_capital_one_csv(csv_path)


def test_invalid_date_format(tmp_path: Path) -> None:
    csv_path = write_sample_csv(
        tmp_path,
        "Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit\n"
        "invalid-date,2026-01-01,1234,TEST,Food,10.00,\n",
    )

    with pytest.raises(ValueError, match=r"Line 2:.*Invalid isoformat string"):
        load_capital_one_csv(csv_path)


def test_empty_debit_and_credit_raises(tmp_path: Path) -> None:
    csv_path = write_sample_csv(
        tmp_path,
        "Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit\n"
        "2026-01-01,2026-01-02,1234,TEST,Food, , \n",
    )

    with pytest.raises(ValueError, match=r"Line 2: Both Debit and Credit are empty"):
        load_capital_one_csv(csv_path)


def test_non_numeric_amount_raises(tmp_path: Path) -> None:
    csv_path = write_sample_csv(
        tmp_path,
        "Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit\n"
        "2026-01-01,2026-01-02,1234,TEST,Food,not-a-number,\n",
    )

    with pytest.raises(ValueError, match=r"Line 2:"):
        load_capital_one_csv(csv_path)


def test_truncated_row_raises(tmp_path: Path) -> None:
    """Simulates a download cut off mid-line where trailing columns become None."""
    csv_path = write_sample_csv(
        tmp_path,
        "Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit\n"
        "2026-01-01,2026-01-02,1234,PARTIAL ROW\n",
    )

    with pytest.raises(ValueError, match=r"Line 2: Both Debit and Credit are empty"):
        load_capital_one_csv(csv_path)


def test_empty_file_raises(tmp_path: Path) -> None:
    csv_path = write_sample_csv(tmp_path, "")

    with pytest.raises(ValueError, match=r"Missing required columns"):
        load_capital_one_csv(csv_path)
