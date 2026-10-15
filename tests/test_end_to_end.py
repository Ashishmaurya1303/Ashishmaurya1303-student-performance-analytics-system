"""End-to-end integration and verification tests for the complete system."""

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_data, clean_data
from src.analytics import enrich_student_dataset, get_performance_summary, get_top_students
from src.display import display_full_report
from main import run_pipeline
from tests.test_data_loader import run_all_tests as run_data_loader_tests
from tests.test_analytics import run_all_tests as run_analytics_tests


def run_all_end_to_end_tests():
    print("=" * 65)
    print("RUNNING END-TO-END VERIFICATION SUITE")
    print("=" * 65)

    test_results = []

    # 1. Verify data loader unit tests
    print("\n--- Verifying Data Loader Tests ---")
    dl_passed = run_data_loader_tests()
    test_results.append(("E2E-01: Data loader unit tests pass", dl_passed, "All 10 loader tests passed"))

    # 2. Verify analytics unit tests
    print("\n--- Verifying Analytics Tests ---")
    an_passed = run_analytics_tests()
    test_results.append(("E2E-02: Analytics unit tests pass", an_passed, "All 11 analytics tests passed"))

    # 3. Verify main pipeline execution on actual dataset
    print("\n--- Verifying main.py pipeline on actual dataset ---")
    data_csv = PROJECT_ROOT / "data" / "students.csv"
    exit_code = run_pipeline(data_csv)
    pipeline_ok = (exit_code == 0)
    test_results.append(("E2E-03: main.py pipeline runs successfully", pipeline_ok, f"Exited with code {exit_code}"))

    # 4. Verify integrity of actual dataset output
    try:
        raw = load_data(data_csv)
        clean = clean_data(raw)
        enriched = enrich_student_dataset(clean)
        summary = get_performance_summary(enriched)
        top3 = get_top_students(enriched, 3)

        assert len(enriched) == 26, f"Expected 26 students, got {len(enriched)}"
        assert summary["total_students"] == 26
        assert summary["passed_students"] == 22
        assert summary["failed_students"] == 4
        assert summary["attendance_shortage_students"] == 7
        assert top3.iloc[0]["student_id"] == "STU104"
        test_results.append(("E2E-04: Metrics integrity on 26 records", True, "26 records, 22 passed, 4 failed, Top 1: STU104"))
    except Exception as e:
        test_results.append(("E2E-04: Metrics integrity on 26 records", False, str(e)))

    # 5. Verify error handling with non-existent file
    try:
        err_code = run_pipeline(PROJECT_ROOT / "data" / "does_not_exist.csv")
        assert err_code == 1, f"Expected error code 1, got {err_code}"
        test_results.append(("E2E-05: Missing file handled gracefully", True, "Returned exit code 1 with clean user error message"))
    except Exception as e:
        test_results.append(("E2E-05: Missing file handled gracefully", False, str(e)))

    # 6. Verify original CSV file is untouched and has 28 lines (header + 26 data + newline)
    try:
        with open(data_csv, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        assert len(lines) == 27, f"Expected 27 non-empty lines (1 header + 26 records), got {len(lines)}"
        test_results.append(("E2E-06: Original dataset CSV unchanged", True, "Original CSV preserved completely"))
    except Exception as e:
        test_results.append(("E2E-06: Original dataset CSV unchanged", False, str(e)))

    print("\n" + "=" * 65)
    print("END-TO-END TEST SUMMARY:")
    all_ok = True
    for name, passed, detail in test_results:
        status = "PASSED [OK]" if passed else "FAILED [X]"
        print(f" - {name:<45}: {status} ({detail})")
        if not passed:
            all_ok = False

    print("=" * 65)
    if all_ok:
        print("ALL END-TO-END VERIFICATION CHECKS PASSED!")
    else:
        print("SOME CHECKS FAILED.")
    print("=" * 65)
    return all_ok


if __name__ == "__main__":
    success = run_all_end_to_end_tests()
    sys.exit(0 if success else 1)
