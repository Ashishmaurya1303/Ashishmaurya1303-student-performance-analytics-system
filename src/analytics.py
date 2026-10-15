"""Analytics module for Student Performance Analytics System.

This module provides pure, vectorized functions using Pandas and NumPy
for computing student totals, averages, grades, pass/fail status,
attendance status, rankings, and statistical cohort summaries.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

# Core subject and threshold constants
SUBJECT_COLUMNS: List[str] = [
    "math_marks",
    "python_marks",
    "data_science_marks",
]

CORE_COLUMNS: List[str] = [
    "student_id",
    "student_name",
    "department",
    "math_marks",
    "python_marks",
    "data_science_marks",
    "attendance_pct",
]

PASSING_MINIMUM_SCORE: float = 40.0
ATTENDANCE_SHORTAGE_THRESHOLD: float = 75.0


def validate_dataframe(df: pd.DataFrame, required_columns: List[str] = None) -> None:
    """Validate that the input is a non-empty DataFrame with required columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    required_columns : List[str], optional
        List of column names required. Defaults to CORE_COLUMNS.

    Raises
    ------
    TypeError
        If input is not a pandas DataFrame.
    ValueError
        If DataFrame is empty or missing required columns.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a pandas DataFrame, got {type(df).__name__}.")

    if df.empty:
        raise ValueError("Input DataFrame is empty. Cannot perform analytics calculations.")

    req_cols = required_columns or CORE_COLUMNS
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Input DataFrame is missing required column(s): {missing}.")


def calculate_total_marks(df: pd.DataFrame) -> pd.Series:
    """Calculate the total marks across Mathematics, Python, and Data Science.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned student dataset.

    Returns
    -------
    pd.Series
        Total marks for each student.
    """
    validate_dataframe(df, SUBJECT_COLUMNS)
    return df[SUBJECT_COLUMNS].sum(axis=1)


def calculate_average_marks(df: pd.DataFrame) -> pd.Series:
    """Calculate average marks (percentage) across all subjects for each student.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned student dataset.

    Returns
    -------
    pd.Series
        Average marks for each student rounded to 2 decimal places.
    """
    validate_dataframe(df, SUBJECT_COLUMNS)
    return df[SUBJECT_COLUMNS].mean(axis=1).round(2)


def determine_pass_fail(df: pd.DataFrame) -> pd.Series:
    """Determine Pass/Fail status for each student.

    Passing Criteria:
    - Score >= 40 marks in EACH individual subject.
    - Overall average >= 40 marks.
    If any subject or average is below 40, status is 'Fail'.

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    pd.Series
        Series containing 'Pass' or 'Fail' for each student.
    """
    validate_dataframe(df, SUBJECT_COLUMNS)
    
    # Check if student passed each individual subject
    all_subjects_passed = (
        (df["math_marks"] >= PASSING_MINIMUM_SCORE)
        & (df["python_marks"] >= PASSING_MINIMUM_SCORE)
        & (df["data_science_marks"] >= PASSING_MINIMUM_SCORE)
    )

    # Check average score
    avg_marks = calculate_average_marks(df)
    avg_passed = avg_marks >= PASSING_MINIMUM_SCORE

    passed = all_subjects_passed & avg_passed
    return pd.Series(np.where(passed, "Pass", "Fail"), index=df.index, name="status")


def assign_grades(df: pd.DataFrame) -> pd.Series:
    """Assign letter grades to students based on passing rules and average marks.

    Grading Scale:
    - Failed student (failed any subject or average < 40): 'F'
    - Average >= 90: 'A+'
    - Average >= 80 and < 90: 'A'
    - Average >= 70 and < 80: 'B'
    - Average >= 60 and < 70: 'C'
    - Average >= 50 and < 60: 'D'
    - Average >= 40 and < 50: 'E'

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    pd.Series
        Assigned letter grade for each student.
    """
    validate_dataframe(df, SUBJECT_COLUMNS)
    
    avg_marks = calculate_average_marks(df)
    status = determine_pass_fail(df)
    is_passed = status == "Pass"

    conditions = [
        ~is_passed,
        avg_marks >= 90.0,
        avg_marks >= 80.0,
        avg_marks >= 70.0,
        avg_marks >= 60.0,
        avg_marks >= 50.0,
        avg_marks >= 40.0,
    ]
    choices = ["F", "A+", "A", "B", "C", "D", "E"]

    grades = np.select(conditions, choices, default="F")
    return pd.Series(grades, index=df.index, name="grade")


def evaluate_attendance(df: pd.DataFrame) -> pd.Series:
    """Evaluate attendance status for each student.

    Rules:
    - Attendance >= 75%: 'Normal'
    - Attendance < 75%: 'Shortage'

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset containing 'attendance_pct'.

    Returns
    -------
    pd.Series
        Attendance status ('Normal' or 'Shortage').
    """
    validate_dataframe(df, ["attendance_pct"])
    status = np.where(
        df["attendance_pct"] >= ATTENDANCE_SHORTAGE_THRESHOLD,
        "Normal",
        "Shortage",
    )
    return pd.Series(status, index=df.index, name="attendance_status")


def enrich_student_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich the student dataset with total, average, status, grade, and attendance status.

    Preserves the original input DataFrame by returning a fresh copy.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned student dataset.

    Returns
    -------
    pd.DataFrame
        Enriched DataFrame with analytical columns appended.
    """
    validate_dataframe(df, CORE_COLUMNS)
    enriched = df.copy(deep=True)

    enriched["total_marks"] = calculate_total_marks(enriched)
    enriched["average_marks"] = calculate_average_marks(enriched)
    enriched["status"] = determine_pass_fail(enriched)
    enriched["grade"] = assign_grades(enriched)
    enriched["attendance_status"] = evaluate_attendance(enriched)

    return enriched


def calculate_subject_averages(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate the class average for each subject.

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    Dict[str, float]
        Dictionary mapping subject name to its rounded class average.
    """
    validate_dataframe(df, SUBJECT_COLUMNS)
    return {
        col: round(float(df[col].mean()), 2)
        for col in SUBJECT_COLUMNS
    }


def calculate_overall_average(df: pd.DataFrame) -> float:
    """Calculate the overall class average across all subjects.

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    float
        Overall class average rounded to 2 decimal places.
    """
    validate_dataframe(df, SUBJECT_COLUMNS)
    # Mean of all subject marks across the entire cohort
    overall_mean = float(df[SUBJECT_COLUMNS].values.mean())
    return round(overall_mean, 2)


def get_top_students(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Identify the top N performing students based on average marks.

    Tie-breaking Rule:
    When students have identical average marks, ties are resolved deterministically by:
    1. total_marks (descending)
    2. math_marks (descending)
    3. python_marks (descending)
    4. data_science_marks (descending)
    5. student_id (ascending)

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset (enriched or clean).
    n : int, default 3
        Number of top students to retrieve.

    Returns
    -------
    pd.DataFrame
        Top N student records sorted by rank.
    """
    enriched = enrich_student_dataset(df) if "average_marks" not in df.columns else df.copy()

    sort_order = ["average_marks", "total_marks", "math_marks", "python_marks", "data_science_marks", "student_id"]
    ascending_flags = [False, False, False, False, False, True]

    sorted_df = enriched.sort_values(by=sort_order, ascending=ascending_flags)
    return sorted_df.head(n)


def get_highest_performing(df: pd.DataFrame) -> pd.DataFrame:
    """Retrieve the student(s) with the highest average marks.

    Handles ties by returning all students who share the maximum average marks.

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    pd.DataFrame
        DataFrame of top performer(s).
    """
    enriched = enrich_student_dataset(df) if "average_marks" not in df.columns else df.copy()
    max_avg = enriched["average_marks"].max()
    return enriched[enriched["average_marks"] == max_avg]


def get_lowest_performing(df: pd.DataFrame) -> pd.DataFrame:
    """Retrieve the student(s) with the lowest average marks.

    Handles ties by returning all students who share the minimum average marks.

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    pd.DataFrame
        DataFrame of lowest performer(s).
    """
    enriched = enrich_student_dataset(df) if "average_marks" not in df.columns else df.copy()
    min_avg = enriched["average_marks"].min()
    return enriched[enriched["average_marks"] == min_avg]


def get_performance_extremes(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Retrieve both the highest-performing and lowest-performing students.

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        A tuple of (highest_performing_df, lowest_performing_df).
    """
    return get_highest_performing(df), get_lowest_performing(df)


def get_performance_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a comprehensive statistical summary of the student cohort.

    Calculates:
    - total_students
    - passed_count & pass_percentage
    - failed_count & fail_percentage
    - shortage_count & shortage_percentage
    - overall_class_average
    - subject_averages

    Parameters
    ----------
    df : pd.DataFrame
        Student dataset.

    Returns
    -------
    Dict[str, Any]
        Dictionary of cohort statistics and counts.
    """
    enriched = enrich_student_dataset(df) if "status" not in df.columns else df.copy()
    total_count = len(enriched)

    if total_count == 0:
        raise ValueError("Cannot generate summary for an empty dataset.")

    passed_count = int((enriched["status"] == "Pass").sum())
    failed_count = int((enriched["status"] == "Fail").sum())
    shortage_count = int((enriched["attendance_status"] == "Shortage").sum())

    pass_pct = round((passed_count / total_count) * 100, 2)
    fail_pct = round((failed_count / total_count) * 100, 2)
    shortage_pct = round((shortage_count / total_count) * 100, 2)

    return {
        "total_students": total_count,
        "passed_students": passed_count,
        "pass_percentage": pass_pct,
        "failed_students": failed_count,
        "fail_percentage": fail_pct,
        "attendance_shortage_students": shortage_count,
        "attendance_shortage_percentage": shortage_pct,
        "overall_class_average": calculate_overall_average(enriched),
        "subject_averages": calculate_subject_averages(enriched),
    }
