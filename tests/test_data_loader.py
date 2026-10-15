"""Automated verification tests for src/data_loader.py."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path so src can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_data, clean_data, REQUIRED_COLUMNS


def run_all_tests():
    data_csv_path = PROJECT_ROOT / "data" / "students.csv"
    test_results = []

    print("=" * 60)
    print("RUNNING VERIFICATION TESTS FOR src/data_loader.py")
    print("=" * 60)

    # -------------------------------------------------------------
    # Test Case 1: Normal dataset loads successfully
    # -------------------------------------------------------------
    try:
        raw_df = load_data(data_csv_path)
        assert isinstance(raw_df, pd.DataFrame), "Result is not a DataFrame"
        test_results.append(("TC-01: Normal dataset loads successfully", True, "Loaded DataFrame successfully"))
    except Exception as e:
        test_results.append(("TC-01: Normal dataset loads successfully", False, str(e)))
        return test_results

    # -------------------------------------------------------------
    # Test Case 2: All expected columns are present
    # -------------------------------------------------------------
    try:
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in raw_df.columns]
        assert len(missing_cols) == 0, f"Missing columns: {missing_cols}"
        test_results.append(("TC-02: All expected columns present", True, f"All {len(REQUIRED_COLUMNS)} columns present"))
    except Exception as e:
        test_results.append(("TC-02: All expected columns present", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 3: The dataset contains at least 20 records
    # -------------------------------------------------------------
    try:
        record_count = len(raw_df)
        assert record_count >= 20, f"Record count {record_count} is less than 20"
        test_results.append(("TC-03: Dataset contains at least 20 records", True, f"Found {record_count} records"))
    except Exception as e:
        test_results.append(("TC-03: Dataset contains at least 20 records", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 4: Valid marks and attendance remain unchanged
    # -------------------------------------------------------------
    try:
        cleaned_df = clean_data(raw_df)
        for col in ["math_marks", "python_marks", "data_science_marks", "attendance_pct"]:
            np.testing.assert_array_almost_equal(
                raw_df[col].astype(float).values,
                cleaned_df[col].values,
                err_msg=f"Column {col} modified unexpectedly"
            )
        test_results.append(("TC-04: Valid marks and attendance remain unchanged", True, "All valid numbers preserved exactly"))
    except Exception as e:
        test_results.append(("TC-04: Valid marks and attendance remain unchanged", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 5: Missing numerical values handled via documented median policy
    # -------------------------------------------------------------
    try:
        sample_df = pd.DataFrame({
            "student_id": ["STU01", "STU02", "STU03"],
            "student_name": ["Alice", "Bob", "Charlie"],
            "department": ["CS", "AI", "IT"],
            "math_marks": [80, np.nan, 100],  # median of [80, 100] is 90
            "python_marks": [70, 80, 90],
            "data_science_marks": [60, 70, 80],
            "attendance_pct": [85.0, 90.0, np.nan]  # median of [85, 90] is 87.5
        })
        cleaned_sample = clean_data(sample_df)
        assert cleaned_sample.loc[1, "math_marks"] == 90.0, f"Expected 90.0, got {cleaned_sample.loc[1, 'math_marks']}"
        assert cleaned_sample.loc[2, "attendance_pct"] == 87.5, f"Expected 87.5, got {cleaned_sample.loc[2, 'attendance_pct']}"
        test_results.append(("TC-05: Missing numerical values imputed with median", True, "NaNs accurately imputed with column median"))
    except Exception as e:
        test_results.append(("TC-05: Missing numerical values imputed with median", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 6: Out-of-range marks and attendance detected & handled
    # -------------------------------------------------------------
    try:
        sample_out_of_range = pd.DataFrame({
            "student_id": ["STU01", "STU02", "STU03"],
            "student_name": ["Alice", "Bob", "Charlie"],
            "department": ["CS", "AI", "IT"],
            "math_marks": [50.0, 150.0, 70.0],  # 150.0 is out of range; median of [50, 70] is 60.0
            "python_marks": [60.0, 70.0, -20.0],  # -20.0 is out of range; median of [60, 70] is 65.0
            "data_science_marks": [80.0, 85.0, 90.0],
            "attendance_pct": [75.0, 80.0, 110.0]  # 110.0 is out of range; median of [75, 80] is 77.5
        })
        cleaned_oor = clean_data(sample_out_of_range)
        assert cleaned_oor.loc[1, "math_marks"] == 60.0, f"Expected imputed 60.0, got {cleaned_oor.loc[1, 'math_marks']}"
        assert cleaned_oor.loc[2, "python_marks"] == 65.0, f"Expected imputed 65.0, got {cleaned_oor.loc[2, 'python_marks']}"
        assert cleaned_oor.loc[2, "attendance_pct"] == 77.5, f"Expected imputed 77.5, got {cleaned_oor.loc[2, 'attendance_pct']}"
        test_results.append(("TC-06: Out-of-range marks and attendance detected & handled", True, "Out-of-range values flagged and imputed with median"))
    except Exception as e:
        test_results.append(("TC-06: Out-of-range marks and attendance detected & handled", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 7: Duplicate IDs detected
    # -------------------------------------------------------------
    try:
        sample_dup = pd.DataFrame({
            "student_id": ["STU01", "STU01", "STU02"],
            "student_name": ["Alice", "Bob", "Charlie"],
            "department": ["CS", "AI", "IT"],
            "math_marks": [80, 85, 90],
            "python_marks": [70, 75, 80],
            "data_science_marks": [60, 65, 70],
            "attendance_pct": [85.0, 80.0, 90.0]
        })
        threw_error = False
        try:
            clean_data(sample_dup)
        except ValueError as ve:
            if "Duplicate student IDs detected" in str(ve):
                threw_error = True
        assert threw_error, "Failed to raise ValueError for duplicate student IDs"
        test_results.append(("TC-07: Duplicate IDs detected", True, "Raised clear ValueError on duplicate student IDs"))
    except Exception as e:
        test_results.append(("TC-07: Duplicate IDs detected", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 8: Missing file produces a clear error
    # -------------------------------------------------------------
    try:
        threw_file_error = False
        try:
            load_data(PROJECT_ROOT / "data" / "non_existent_file.csv")
        except FileNotFoundError as fnf:
            threw_file_error = True
        assert threw_file_error, "Failed to raise FileNotFoundError for missing file"
        test_results.append(("TC-08: Missing file produces clear error", True, "Raised FileNotFoundError with helpful path message"))
    except Exception as e:
        test_results.append(("TC-08: Missing file produces clear error", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 9: Missing required columns produce a clear error
    # -------------------------------------------------------------
    try:
        dummy_path = PROJECT_ROOT / "data" / "temp_missing_col.csv"
        pd.DataFrame({
            "student_id": ["STU01"],
            "student_name": ["Alice"],
            "math_marks": [90]
        }).to_csv(dummy_path, index=False)

        threw_col_error = False
        try:
            load_data(dummy_path)
        except ValueError as ve:
            if "missing required column" in str(ve).lower():
                threw_col_error = True
        finally:
            if dummy_path.exists():
                dummy_path.unlink()

        assert threw_col_error, "Failed to raise ValueError for missing required columns"
        test_results.append(("TC-09: Missing required columns produce clear error", True, "Raised ValueError identifying missing columns"))
    except Exception as e:
        test_results.append(("TC-09: Missing required columns produce clear error", False, str(e)))

    # -------------------------------------------------------------
    # Test Case 10: Original DataFrame remains unchanged after cleaning
    # -------------------------------------------------------------
    try:
        original_df = pd.DataFrame({
            "student_id": ["STU01", "STU02"],
            "student_name": ["  Alice  ", "Bob"],
            "department": ["CS ", "AI"],
            "math_marks": [80, np.nan],
            "python_marks": [70, 85],
            "data_science_marks": [60, 75],
            "attendance_pct": [85.0, 90.0]
        })
        original_df_copy = original_df.copy(deep=True)
        _ = clean_data(original_df)
        pd.testing.assert_frame_equal(original_df, original_df_copy)
        test_results.append(("TC-10: Original DataFrame remains unchanged", True, "Input DataFrame is completely immutable"))
    except Exception as e:
        test_results.append(("TC-10: Original DataFrame remains unchanged", False, str(e)))

    # Print summary
    print("\nTEST SUMMARY:")
    all_passed = True
    for name, passed, detail in test_results:
        status = "PASSED [OK]" if passed else "FAILED [X]"
        print(f" - {name:<55}: {status} ({detail})")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL 10 TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 60)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
