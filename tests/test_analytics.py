"""Automated verification tests for src/analytics.py."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path so src can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analytics import (
    calculate_total_marks,
    calculate_average_marks,
    determine_pass_fail,
    assign_grades,
    evaluate_attendance,
    enrich_student_dataset,
    calculate_subject_averages,
    calculate_overall_average,
    get_top_students,
    get_highest_performing,
    get_lowest_performing,
    get_performance_extremes,
    get_performance_summary,
)


def create_base_sample_df() -> pd.DataFrame:
    """Helper to create a controlled test DataFrame."""
    return pd.DataFrame({
        "student_id": ["S01", "S02", "S03", "S04"],
        "student_name": ["Alice", "Bob", "Charlie", "David"],
        "department": ["CS", "AI", "IT", "DS"],
        "math_marks": [80.0, 90.0, 70.0, 60.0],
        "python_marks": [85.0, 95.0, 75.0, 65.0],
        "data_science_marks": [90.0, 85.0, 80.0, 70.0],
        "attendance_pct": [92.0, 74.5, 75.0, 88.0],
    })


def run_all_tests():
    test_results = []
    print("=" * 65)
    print("RUNNING VERIFICATION TESTS FOR src/analytics.py")
    print("=" * 65)

    # -------------------------------------------------------------------------
    # TC-01: Correct totals and averages
    # -------------------------------------------------------------------------
    try:
        df = create_base_sample_df()
        totals = calculate_total_marks(df)
        averages = calculate_average_marks(df)

        expected_totals = [255.0, 270.0, 225.0, 195.0]
        expected_averages = [85.0, 90.0, 75.0, 65.0]

        np.testing.assert_array_almost_equal(totals.values, expected_totals)
        np.testing.assert_array_almost_equal(averages.values, expected_averages)
        test_results.append(("TC-01: Correct totals and averages", True, "Totals and averages match exact values"))
    except Exception as e:
        test_results.append(("TC-01: Correct totals and averages", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-02: Every grade boundary (90, 80, 70, 60, 50, 40, <40)
    # -------------------------------------------------------------------------
    try:
        boundary_df = pd.DataFrame({
            "student_id": [f"B0{i}" for i in range(1, 8)],
            "student_name": ["G_Aplus", "G_A", "G_B", "G_C", "G_D", "G_E", "G_F"],
            "department": ["CS"] * 7,
            # Each subject equal to average so subject-pass is met when avg >= 40
            "math_marks": [90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 39.9],
            "python_marks": [90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 39.9],
            "data_science_marks": [90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 39.9],
            "attendance_pct": [80.0] * 7,
        })
        grades = assign_grades(boundary_df).tolist()
        expected_grades = ["A+", "A", "B", "C", "D", "E", "F"]
        assert grades == expected_grades, f"Expected {expected_grades}, got {grades}"
        test_results.append(("TC-02: Every grade boundary accurate", True, f"Boundary grades verified: {grades}"))
    except Exception as e:
        test_results.append(("TC-02: Every grade boundary accurate", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-03: Student who fails one subject despite high average
    # -------------------------------------------------------------------------
    try:
        fail_sub_df = pd.DataFrame({
            "student_id": ["FS01"],
            "student_name": ["FailingInMath"],
            "department": ["AI"],
            "math_marks": [35.0],  # Fails math (<40)
            "python_marks": [95.0],
            "data_science_marks": [95.0],
            "attendance_pct": [90.0],
        })
        # Average is (35 + 95 + 95) / 3 = 75.0 (normally grade B)
        status = determine_pass_fail(fail_sub_df).iloc[0]
        grade = assign_grades(fail_sub_df).iloc[0]
        assert status == "Fail", f"Expected Fail status, got {status}"
        assert grade == "F", f"Expected Grade F, got {grade}"
        test_results.append(("TC-03: Single subject failure overrides high average", True, "Status is Fail and Grade is F despite 75.0 average"))
    except Exception as e:
        test_results.append(("TC-03: Single subject failure overrides high average", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-04: Pass/Fail classification
    # -------------------------------------------------------------------------
    try:
        pf_df = pd.DataFrame({
            "student_id": ["P01", "P02", "P03"],
            "student_name": ["AllPass", "BorderPass", "BelowAvgFail"],
            "department": ["CS", "AI", "DS"],
            "math_marks": [60.0, 40.0, 39.0],
            "python_marks": [60.0, 40.0, 40.0],
            "data_science_marks": [60.0, 40.0, 40.0],
            "attendance_pct": [80.0, 80.0, 80.0],
        })
        statuses = determine_pass_fail(pf_df).tolist()
        expected = ["Pass", "Pass", "Fail"]
        assert statuses == expected, f"Expected {expected}, got {statuses}"
        test_results.append(("TC-04: Pass/Fail classification", True, f"Classifications verified: {statuses}"))
    except Exception as e:
        test_results.append(("TC-04: Pass/Fail classification", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-05: Attendance at 74.5% vs exactly 75.0%
    # -------------------------------------------------------------------------
    try:
        att_df = pd.DataFrame({
            "student_id": ["A01", "A02"],
            "student_name": ["JustBelow", "ExactBorder"],
            "department": ["IT", "IT"],
            "math_marks": [70.0, 70.0],
            "python_marks": [70.0, 70.0],
            "data_science_marks": [70.0, 70.0],
            "attendance_pct": [74.5, 75.0],
        })
        att_status = evaluate_attendance(att_df).tolist()
        assert att_status == ["Shortage", "Normal"], f"Expected ['Shortage', 'Normal'], got {att_status}"
        test_results.append(("TC-05: Attendance boundary (74.5% vs 75.0%)", True, "74.5% is Shortage, 75.0% is Normal"))
    except Exception as e:
        test_results.append(("TC-05: Attendance boundary (74.5% vs 75.0%)", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-06: Subject-wise and overall class averages
    # -------------------------------------------------------------------------
    try:
        calc_df = pd.DataFrame({
            "student_id": ["C1", "C2"],
            "student_name": ["A", "B"],
            "department": ["CS", "CS"],
            "math_marks": [60.0, 80.0],           # mean = 70.0
            "python_marks": [50.0, 70.0],         # mean = 60.0
            "data_science_marks": [90.0, 100.0],  # mean = 95.0
            "attendance_pct": [80.0, 90.0],
        })
        sub_avgs = calculate_subject_averages(calc_df)
        overall_avg = calculate_overall_average(calc_df)

        assert sub_avgs["math_marks"] == 70.0
        assert sub_avgs["python_marks"] == 60.0
        assert sub_avgs["data_science_marks"] == 95.0
        # (70 + 60 + 95) / 3 = 225 / 3 = 75.0
        assert overall_avg == 75.0
        test_results.append(("TC-06: Subject-wise and overall averages", True, f"Subject: {sub_avgs}, Overall: {overall_avg}"))
    except Exception as e:
        test_results.append(("TC-06: Subject-wise and overall averages", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-07: Top 3 ranking and deterministic tie-breaking
    # -------------------------------------------------------------------------
    try:
        rank_df = pd.DataFrame({
            "student_id": ["T01", "T02", "T03", "T04"],
            "student_name": ["TieBob", "TieAlice", "Lower", "Leader"],
            "department": ["CS", "CS", "CS", "CS"],
            # T04 is distinct leader (avg 95)
            # T01 and T02 have exact same average (85.0), but T01 has higher math marks (90 vs 80)
            "math_marks": [90.0, 80.0, 50.0, 95.0],
            "python_marks": [80.0, 90.0, 50.0, 95.0],
            "data_science_marks": [85.0, 85.0, 50.0, 95.0],
            "attendance_pct": [80.0, 80.0, 80.0, 80.0],
        })
        top3 = get_top_students(rank_df, n=3)
        top3_ids = top3["student_id"].tolist()
        # Leader is T04, then T01 (higher math), then T02
        assert top3_ids == ["T04", "T01", "T02"], f"Expected ['T04', 'T01', 'T02'], got {top3_ids}"
        test_results.append(("TC-07: Top 3 ranking and tie-break rule", True, f"Top 3 order verified: {top3_ids}"))
    except Exception as e:
        test_results.append(("TC-07: Top 3 ranking and tie-break rule", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-08: Highest and lowest performing students
    # -------------------------------------------------------------------------
    try:
        sample_df = create_base_sample_df()
        highest_df = get_highest_performing(sample_df)
        lowest_df = get_lowest_performing(sample_df)

        assert highest_df.iloc[0]["student_id"] == "S02"  # Bob has avg 90.0
        assert lowest_df.iloc[0]["student_id"] == "S04"   # David has avg 65.0

        extremes_high, extremes_low = get_performance_extremes(sample_df)
        assert extremes_high.iloc[0]["student_id"] == "S02"
        assert extremes_low.iloc[0]["student_id"] == "S04"
        test_results.append(("TC-08: Highest and lowest performers", True, "Highest is S02 (90.0), Lowest is S04 (65.0)"))
    except Exception as e:
        test_results.append(("TC-08: Highest and lowest performers", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-09: Empty DataFrame and missing required columns validation
    # -------------------------------------------------------------------------
    try:
        empty_df = pd.DataFrame()
        threw_empty = False
        try:
            calculate_total_marks(empty_df)
        except ValueError:
            threw_empty = True

        missing_col_df = pd.DataFrame({"math_marks": [80.0]})
        threw_missing = False
        try:
            enrich_student_dataset(missing_col_df)
        except ValueError:
            threw_missing = True

        assert threw_empty, "Failed to reject empty DataFrame"
        assert threw_missing, "Failed to reject DataFrame with missing columns"
        test_results.append(("TC-09: Empty DataFrame & missing columns rejected", True, "Proper ValueErrors raised"))
    except Exception as e:
        test_results.append(("TC-09: Empty DataFrame & missing columns rejected", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-10: Original DataFrame remains unchanged
    # -------------------------------------------------------------------------
    try:
        original = create_base_sample_df()
        original_copy = original.copy(deep=True)
        _ = enrich_student_dataset(original)
        pd.testing.assert_frame_equal(original, original_copy)
        test_results.append(("TC-10: Original DataFrame immutability preserved", True, "Input DataFrame unchanged after enrichment"))
    except Exception as e:
        test_results.append(("TC-10: Original DataFrame immutability preserved", False, str(e)))

    # -------------------------------------------------------------------------
    # TC-11: Overall performance summary calculation
    # -------------------------------------------------------------------------
    try:
        sample_df = create_base_sample_df()
        summary = get_performance_summary(sample_df)
        assert summary["total_students"] == 4
        assert summary["passed_students"] == 4
        assert summary["failed_students"] == 0
        assert summary["attendance_shortage_students"] == 1  # Bob (74.5%)
        assert summary["attendance_shortage_percentage"] == 25.0
        test_results.append(("TC-11: Performance summary verification", True, f"Summary counts and percentages accurate"))
    except Exception as e:
        test_results.append(("TC-11: Performance summary verification", False, str(e)))

    # Print summary
    print("\nTEST SUMMARY:")
    all_passed = True
    for name, passed, detail in test_results:
        status = "PASSED [OK]" if passed else "FAILED [X]"
        print(f" - {name:<55}: {status} ({detail})")
        if not passed:
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("ALL ANALYTICS TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 65)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
