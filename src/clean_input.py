import os
import pandas as pd

def process_capital_one_file(file_path: str) -> pd.DataFrame:
    """
    Function to process Capital One CSV files

    Args:
        file_path: Path to the CSV file to process

    Returns:
        pd.Dataframe: Cleaned and validated transaction data

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: if the file has invalid format or content
    """

    # 1. Verify file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at {file_path}")

    # 2. Load data with proper encoding
    try:
        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            on_bad_lines='skip'
        )
    except Exception as e:
        raise ValueError(f"Error loading CSV: {e!s}")

    # 3. Validate required columns
    required_columns = [
        "Transaction Date",
        "Posted Date",
        "Card No.",
        "Description",
        "Category",
        "Debit",
        "Credit",
    ]
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # 4. Parse dates
    for date_col in ["Transaction Date", "Posted Date"]:
        df[date_col] = pd.to_datetime(df[date_col], errors="raise")

    # 5. Convert numeric columns
    df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce")
    df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce")

    # 6. Compute signed amount
    df["Amount"] = df.apply(
        lambda row: -row["Debit"] if not pd.isna(row["Debit"]) else row["Credit"],
        axis=1,
    )

    # 7. Drop original Debit/Credit columns
    df = df.drop(columns=["Debit", "Credit"])

    # 8. Reorder columns
    df = df[[
        "Transaction Date",
        "Posted Date",
        "Card No.",
        "Description",
        "Category",
        "Amount",
    ]]

    # 9. Ensure no missing critical data
    if df["Amount"].isna().any():
        raise ValueError("Amount column contains NaN values after processing.")

    return df
