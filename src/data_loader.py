"""Data loading and cleaning module for Student Performance Analytics System.

This module provides robust functions to load student data from a CSV file
and clean/validate the dataset for downstream analytics without altering
the original data structures or silently corrupting invalid data.
"""

from pathlib import Path
from typing import List, Union
import numpy as np
import pandas as pd

# Required schema columns
REQUIRED_COLUMNS: List[str] = [
    "student_id",
    "student_name",
    "department",
    "math_marks",
    "python_marks",
    "data_science_marks",
    "attendance_pct",
]

# Numeric columns and their valid ranges
NUMERIC_COLUMNS: List[str] = [
    "math_marks",
    "python_marks",
    "data_science_marks",
    "attendance_pct",
]

MIN_SCORE: float = 0.0
MAX_SCORE: float = 100.0


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load student data from a CSV file into a Pandas DataFrame.

    Parameters
    ----------
    file_path : Union[str, Path]
        The path to the CSV file to load.

    Returns
    -------
    pd.DataFrame
        Loaded student data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the specified path.
    ValueError
        If the file is empty, malformed, or missing required columns.
    """
    path = Path(file_path)

    # 1. Check if the file exists
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at: '{path.resolve()}'")

    if not path.is_file():
        raise ValueError(f"Specified path is not a file: '{path.resolve()}'")

    # 2. Check if file is empty (0 bytes)
    if path.stat().st_size == 0:
        raise ValueError(f"The dataset file is empty (0 bytes): '{path.name}'")

    # 3. Read the CSV file
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"The dataset file contains no readable data: '{path.name}'")
    except pd.errors.ParserError as e:
        raise ValueError(f"Failed to parse CSV file due to formatting errors: {e}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file '{path.name}': {e}")

    # 4. Check if DataFrame is empty after reading
    if df.empty:
        raise ValueError(f"The dataset file contains headers but no data records: '{path.name}'")

    # 5. Verify required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required column(s): {missing_columns}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the student dataset.

    Cleaning and Validation Policy:
    1. Input validation: Input must be a non-empty pandas DataFrame.
    2. Immutability: The original input DataFrame is never mutated; a deep copy is returned.
    3. String fields: Strip leading and trailing whitespace. Empty or null names/IDs raise an error.
    4. Unique Identity: Duplicate student IDs are detected and raise a ValueError.
    5. Numeric coercion: Marks and attendance are safely converted to numeric types.
    6. Range validation: Marks and attendance must be between 0.0 and 100.0. Values outside
       this range are treated as invalid and converted to NaN for transparent imputation.
    7. Imputation Policy: Missing or invalid numerical values are imputed using the valid
       column median. If a column has no valid values to calculate a median, a ValueError is raised.
       All imputations are logged/printed transparently.

    Parameters
    ----------
    df : pd.DataFrame
        Raw student dataset.

    Returns
    -------
    pd.DataFrame
        Cleaned and validated DataFrame ready for analytics.

    Raises
    ------
    TypeError
        If the input is not a pandas DataFrame.
    ValueError
        If DataFrame is empty, contains duplicate IDs, missing required fields,
        or cannot compute medians for missing columns.
    """
    # 1. Validate input type and non-emptiness
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Input data must be a pandas DataFrame, got {type(df).__name__}.")

    if df.empty:
        raise ValueError("Input DataFrame is empty. Cannot perform cleaning.")

    # 2. Check presence of required columns before processing
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {missing_columns}")

    # 3. Preserve the original DataFrame (immutability)
    cleaned_df = df.copy()

    # 4. Clean text fields (strip whitespace)
    text_columns = ["student_id", "student_name", "department"]
    for col in text_columns:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

    # 5. Check for missing or empty student IDs
    invalid_id_mask = (
        cleaned_df["student_id"].isna()
        | (cleaned_df["student_id"] == "")
        | (cleaned_df["student_id"].str.lower() == "nan")
        | (cleaned_df["student_id"].str.lower() == "none")
    )
    if invalid_id_mask.any():
        invalid_rows = cleaned_df[invalid_id_mask].index.tolist()
        raise ValueError(
            f"Dataset contains empty or null 'student_id' at row index(es): {invalid_rows}."
        )

    # 6. Check for missing or empty student names
    invalid_name_mask = (
        cleaned_df["student_name"].isna()
        | (cleaned_df["student_name"] == "")
        | (cleaned_df["student_name"].str.lower() == "nan")
        | (cleaned_df["student_name"].str.lower() == "none")
    )
    if invalid_name_mask.any():
        invalid_rows = cleaned_df[invalid_name_mask].index.tolist()
        raise ValueError(
            f"Dataset contains empty or null 'student_name' at row index(es): {invalid_rows}."
        )

    # 7. Check for duplicate student IDs
    duplicate_mask = cleaned_df["student_id"].duplicated(keep=False)
    if duplicate_mask.any():
        duplicate_ids = sorted(cleaned_df.loc[duplicate_mask, "student_id"].unique().tolist())
        raise ValueError(
            f"Duplicate student IDs detected: {duplicate_ids}. "
            "Each student must have a unique identifier."
        )

    # 8. Numeric conversion, range validation, and documented median imputation
    for col in NUMERIC_COLUMNS:
        # Convert to numeric safely; non-numeric strings become NaN
        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")

        # Flag out-of-range values (< 0 or > 100)
        out_of_range_mask = (cleaned_df[col] < MIN_SCORE) | (cleaned_df[col] > MAX_SCORE)
        if out_of_range_mask.any():
            invalid_indices = cleaned_df[out_of_range_mask].index.tolist()
            invalid_values = cleaned_df.loc[out_of_range_mask, col].tolist()
            print(
                f"[Data Cleaning Notice] Out-of-range value(s) detected in '{col}': "
                f"{invalid_values} at index(es) {invalid_indices}. Flagged for median imputation."
            )
            # Mark out-of-range values as NaN for median imputation
            cleaned_df.loc[out_of_range_mask, col] = np.nan

        # Handle missing or flagged NaN values
        nan_mask = cleaned_df[col].isna()
        if nan_mask.any():
            # Calculate median of remaining valid values in this column
            valid_values = cleaned_df.loc[~nan_mask, col]
            if valid_values.empty:
                raise ValueError(
                    f"Column '{col}' contains no valid numeric values to compute a median for imputation."
                )

            median_val = float(valid_values.median())
            impute_val = round(median_val, 2)
            imputed_indices = cleaned_df[nan_mask].index.tolist()

            cleaned_df.loc[nan_mask, col] = impute_val
            print(
                f"[Data Cleaning Notice] Imputed {len(imputed_indices)} missing/invalid value(s) in "
                f"'{col}' at index(es) {imputed_indices} with column median: {impute_val}."
            )

        # Convert marks to float
        cleaned_df[col] = cleaned_df[col].astype(float)

    return cleaned_df
