"""
==========================================================================
DATA PREPARATION HELPER
==========================================================================

This script helps you convert your real-world operational data into the
format that main.py expects.

If you have data in Excel or a simple CSV, this script will:
    1. Read your file (CSV or Excel)
    2. Map your column names to the required format
    3. Calculate missing columns automatically
    4. Save the result as data/operations_data.csv

This way you DON'T need to manually rename all your columns.

Usage:
    python prepare_data.py my_data.csv
    python prepare_data.py my_data.xlsx
    python prepare_data.py my_data.csv --preview   (just preview, don't save)
"""

# ============================================================
# IMPORTS
# ============================================================

import argparse      # For command-line arguments
import json          # For saving pipeline metadata
import sys           # For exiting on errors
from pathlib import Path  # For file path operations

import pandas as pd  # For data manipulation


# ============================================================
# REQUIRED COLUMNS
# These are what main.py expects. Your data doesn't need
# to have these exact names - we'll help you map them.
# ============================================================

REQUIRED_COLUMNS = [
    "case_id",          # Unique ID for each case/order/ticket
    "case_date",        # Date the case started (YYYY-MM-DD)
    "process_step",     # Name of the process step
    "step_number",      # Order of the step (1, 2, 3...)
    "department",       # Which team handles this step
    "employee_id",      # Who worked on it
    "priority",         # Priority level (Standard/Express/Rush)
    "complexity",       # Complexity score (1-10)
    "case_value",       # Dollar value of the case
    "wait_time_min",    # Minutes waiting before step started
    "cycle_time_min",   # Minutes the step took to complete
    "total_time_min",   # wait_time + cycle_time
    "start_time",       # When the step started
    "end_time",         # When the step ended
    "error_count",      # Number of errors (0 or 1)
    "rework_count",     # Rework needed (0 or 1)
    "month",            # Month number (1-12)
    "day_of_week",      # Day name (Monday, Tuesday, etc.)
]


# ============================================================
# COMMON COLUMN NAME MAPPINGS
# Maps common real-world column names to our required names.
# If your data uses any of these names, they'll be auto-mapped.
# ============================================================

COLUMN_ALIASES = {
    # case_id aliases
    "order_id": "case_id",
    "order_number": "case_id",
    "ticket_id": "case_id",
    "ticket_number": "case_id",
    "incident_id": "case_id",
    "po_number": "case_id",
    "request_id": "case_id",
    "id": "case_id",

    # case_date aliases
    "order_date": "case_date",
    "date": "case_date",
    "created_date": "case_date",
    "ticket_date": "case_date",
    "request_date": "case_date",

    # process_step aliases
    "step": "process_step",
    "step_name": "process_step",
    "stage": "process_step",
    "phase": "process_step",
    "activity": "process_step",

    # department aliases
    "dept": "department",
    "team": "department",
    "group": "department",
    "unit": "department",

    # employee_id aliases
    "employee": "employee_id",
    "agent": "employee_id",
    "worker": "employee_id",
    "assigned_to": "employee_id",
    "handler": "employee_id",

    # time aliases
    "wait_time": "wait_time_min",
    "waiting_time": "wait_time_min",
    "queue_time": "wait_time_min",
    "cycle_time": "cycle_time_min",
    "processing_time": "cycle_time_min",
    "duration": "cycle_time_min",
    "total_time": "total_time_min",

    # value aliases
    "value": "case_value",
    "order_value": "case_value",
    "amount": "case_value",
    "cost": "case_value",
}


def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from CSV or Excel file.

    Args:
        file_path: Path to the data file.

    Returns:
        A pandas DataFrame with the loaded data.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        print(f"Error: Unsupported file format: {ext}")
        print("Supported formats: .csv, .xlsx, .xls")
        sys.exit(1)

    print(f"Loaded {len(df):,} rows from {file_path}")
    print(f"Your columns: {list(df.columns)}")
    print()

    return df


def auto_map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Automatically renames columns based on common aliases.

    If your data has columns like "order_id" or "ticket_id",
    they'll be automatically renamed to "case_id", etc.

    Args:
        df: The loaded DataFrame.

    Returns:
        DataFrame with renamed columns.
    """
    # Convert all column names to lowercase for matching
    rename_map = {}
    for col in df.columns:
        col_lower = col.lower().strip().replace(" ", "_")
        if col_lower in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[col_lower]
        elif col_lower in REQUIRED_COLUMNS:
            rename_map[col] = col_lower

    if rename_map:
        print("Auto-mapped columns:")
        for old_name, new_name in rename_map.items():
            if old_name != new_name:
                print(f"  {old_name} -> {new_name}")
        df = df.rename(columns=rename_map)
        print()

    return df


def fill_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates or fills in any missing columns that main.py needs.

    For example:
        - If total_time_min is missing, calculates it from wait + cycle time
        - If month is missing, extracts it from case_date
        - If day_of_week is missing, extracts it from case_date
        - If step_number is missing, assigns numbers based on step order

    Args:
        df: DataFrame with potentially missing columns.

    Returns:
        DataFrame with all required columns filled in.
    """
    print("Checking for missing columns...")

    # --- Fill total_time_min ---
    if "total_time_min" not in df.columns:
        if "wait_time_min" in df.columns and "cycle_time_min" in df.columns:
            df["total_time_min"] = df["wait_time_min"] + df["cycle_time_min"]
            print("  Calculated: total_time_min = wait_time_min + cycle_time_min")

    # --- Fill month and day_of_week from case_date ---
    if "case_date" in df.columns:
        df["case_date"] = pd.to_datetime(df["case_date"])
        if "month" not in df.columns:
            df["month"] = df["case_date"].dt.month
            print("  Extracted: month from case_date")
        if "day_of_week" not in df.columns:
            df["day_of_week"] = df["case_date"].dt.day_name()
            print("  Extracted: day_of_week from case_date")
        # Convert back to string for CSV
        df["case_date"] = df["case_date"].dt.strftime("%Y-%m-%d")

    # --- Fill step_number based on process_step order ---
    if "step_number" not in df.columns and "process_step" in df.columns:
        # Assign step numbers based on first appearance order
        step_order = df["process_step"].unique()
        step_map = {step: i + 1 for i, step in enumerate(step_order)}
        df["step_number"] = df["process_step"].map(step_map)
        print(f"  Assigned step_number based on order: {step_map}")

    # --- Fill start_time and end_time if missing ---
    if "start_time" not in df.columns:
        df["start_time"] = df.get("case_date", "2025-01-01") + " 09:00"
        print("  Filled: start_time with default 09:00")
    if "end_time" not in df.columns:
        df["end_time"] = df.get("case_date", "2025-01-01") + " 10:00"
        print("  Filled: end_time with default 10:00")

    # --- Fill optional columns with defaults ---
    defaults = {
        "priority": "Standard",
        "complexity": 5,
        "case_value": 1000.0,
        "employee_id": "UNKNOWN",
        "department": "General",
        "error_count": 0,
        "rework_count": 0,
        "wait_time_min": 0.0,
    }

    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val
            print(f"  Filled: {col} with default value: {default_val}")

    print()
    return df


def validate_data(df: pd.DataFrame) -> bool:
    """
    Checks that the DataFrame has all required columns
    and the data looks reasonable.

    Args:
        df: The prepared DataFrame.

    Returns:
        True if data is valid, False otherwise.
    """
    print("Validating data...")

    # Check for required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"  ERROR: Missing required columns: {missing_cols}")
        print()
        print("  Your data needs at minimum:")
        print("    - case_id (or order_id/ticket_id)")
        print("    - process_step (or step/stage)")
        print("    - cycle_time_min (or processing_time/duration)")
        print()
        print("  Other columns can be auto-filled with defaults.")
        return False

    # Check for reasonable values
    if df["cycle_time_min"].min() < 0:
        print("  WARNING: Negative cycle times found. These will be set to 0.")
        df.loc[df["cycle_time_min"] < 0, "cycle_time_min"] = 0

    if df["wait_time_min"].min() < 0:
        print("  WARNING: Negative wait times found. These will be set to 0.")
        df.loc[df["wait_time_min"] < 0, "wait_time_min"] = 0

    num_cases = df["case_id"].nunique()
    num_steps = df["process_step"].nunique()
    print(f"  Cases: {num_cases:,}")
    print(f"  Process steps: {num_steps}")
    print(f"  Total records: {len(df):,}")
    print(f"  Date range: {df['case_date'].min()} to {df['case_date'].max()}")
    print("  Validation PASSED")
    print()

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Prepare your real-world data for the Operational Efficiency Scoring System."
    )
    parser.add_argument("file", help="Path to your data file (CSV or Excel)")
    parser.add_argument("--preview", action="store_true",
                        help="Preview the result without saving")
    parser.add_argument("--name", default="Custom Operations Pipeline",
                        help="Name for your pipeline (used in report titles)")
    parser.add_argument("--output", default="data/operations_data.csv",
                        help="Output path (default: data/operations_data.csv)")
    args = parser.parse_args()

    # Check that input file exists
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    print("=" * 60)
    print("DATA PREPARATION HELPER")
    print("=" * 60)
    print()

    # Step 1: Load the data
    df = load_data(args.file)

    # Step 2: Auto-map column names
    df = auto_map_columns(df)

    # Step 3: Fill in missing columns
    df = fill_missing_columns(df)

    # Step 4: Validate
    if not validate_data(df):
        sys.exit(1)

    # Step 5: Preview or save
    if args.preview:
        print("PREVIEW (first 5 rows):")
        print(df.head().to_string(index=False))
        print()
        print("To save, run again without --preview")
    else:
        # Save the CSV
        Path(args.output).parent.mkdir(exist_ok=True)
        df.to_csv(args.output, index=False)
        print(f"Data saved to: {args.output}")

        # Save pipeline metadata
        meta = {"name": args.name, "type": "custom-real-data", "description": f"Real operational data from {args.file}"}
        meta_path = Path(args.output).parent / "pipeline_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print(f"Pipeline metadata saved to: {meta_path}")
        print()
        print("Now run the analysis:")
        print("  python main.py")
        print("  python main.py --with-ai    (for AI recommendations)")


if __name__ == "__main__":
    main()
