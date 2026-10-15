"""Terminal reporting and formatting module for Student Performance Analytics System.

This module provides clean, aligned, and readable terminal output functions
for displaying student records, rankings, subject performance, and statistical summaries.
"""

from typing import Any, Dict, List
import pandas as pd


DIVIDER_LINE = "=" * 90
SECTION_DIVIDER = "-" * 90
SUB_DIVIDER = "-" * 45


def display_header() -> None:
    """Display the application title banner and introduction."""
    print("\n" + DIVIDER_LINE)
    print("           STUDENT PERFORMANCE ANALYTICS SYSTEM           ")
    print("          Powered by Python, Pandas, and NumPy             ")
    print(DIVIDER_LINE)
    print("  This system analyzes academic performance, attendance records, and generates")
    print("  actionable insights for educators and departmental coordinators.")
    print(DIVIDER_LINE + "\n")


def display_student_table(df: pd.DataFrame) -> None:
    """Display the formatted student performance table.

    Parameters
    ----------
    df : pd.DataFrame
        Enriched DataFrame containing student records and analytics metrics.
    """
    print(SECTION_DIVIDER)
    print(" 1. COMPLETE STUDENT PERFORMANCE ROSTER")
    print(SECTION_DIVIDER)

    if df.empty:
        print("  [Notice] No student records available to display.")
        print(SECTION_DIVIDER + "\n")
        return

    # Header row
    header = (
        f"{'ID':<8} "
        f"{'Name':<18} "
        f"{'Department':<23} "
        f"{'Math':>6} "
        f"{'Pyth':>6} "
        f"{'DS':>6} "
        f"{'Total':>7} "
        f"{'Avg %':>7} "
        f"{'Grd':^5} "
        f"{'Status':^6} "
        f"{'Att %':>6} "
        f"{'Att Stat':^8}"
    )
    print(header)
    print("-" * len(header))

    # Data rows
    for _, row in df.iterrows():
        math = f"{row['math_marks']:.1f}"
        pyth = f"{row['python_marks']:.1f}"
        ds = f"{row['data_science_marks']:.1f}"
        total = f"{row['total_marks']:.1f}"
        avg = f"{row['average_marks']:.2f}"
        att = f"{row['attendance_pct']:.1f}"

        line = (
            f"{str(row['student_id']):<8} "
            f"{str(row['student_name'])[:18]:<18} "
            f"{str(row['department'])[:23]:<23} "
            f"{math:>6} "
            f"{pyth:>6} "
            f"{ds:>6} "
            f"{total:>7} "
            f"{avg:>7} "
            f"{str(row['grade']):^5} "
            f"{str(row['status']):^6} "
            f"{att:>6} "
            f"{str(row['attendance_status']):^8}"
        )
        print(line)

    print("-" * len(header))
    print(f" Total records displayed: {len(df)}\n")


def display_top_performers(top_df: pd.DataFrame) -> None:
    """Display the top-performing students.

    Parameters
    ----------
    top_df : pd.DataFrame
        DataFrame of top performers sorted by rank.
    """
    print(SECTION_DIVIDER)
    print(" 2. TOP PERFORMING STUDENTS (HONOR ROLL)")
    print(SECTION_DIVIDER)

    if top_df.empty:
        print("  [Notice] No top performers to display.")
        print(SECTION_DIVIDER + "\n")
        return

    header = f"{'Rank':<6} {'ID':<8} {'Name':<20} {'Department':<24} {'Total':>7} {'Average %':>10} {'Grade':^7}"
    print(header)
    print("-" * len(header))

    rank = 1
    for _, row in top_df.iterrows():
        medal = f"#{rank}"
        print(
            f"{medal:<6} "
            f"{str(row['student_id']):<8} "
            f"{str(row['student_name'])[:20]:<20} "
            f"{str(row['department'])[:24]:<24} "
            f"{row['total_marks']:>7.1f} "
            f"{row['average_marks']:>9.2f}% "
            f"{str(row['grade']):^7}"
        )
        rank += 1

    print("-" * len(header) + "\n")


def display_performance_extremes(highest_df: pd.DataFrame, lowest_df: pd.DataFrame) -> None:
    """Display the highest and lowest performing students, including ties.

    Parameters
    ----------
    highest_df : pd.DataFrame
        DataFrame containing student(s) with maximum average marks.
    lowest_df : pd.DataFrame
        DataFrame containing student(s) with minimum average marks.
    """
    print(SECTION_DIVIDER)
    print(" 3. HIGHEST AND LOWEST PERFORMERS (CLASS EXTREMES)")
    print(SECTION_DIVIDER)

    print(" Highest Performer(s):")
    if highest_df.empty:
        print("   No records available.")
    else:
        for _, row in highest_df.iterrows():
            print(
                f"   * {row['student_name']} ({row['student_id']}, {row['department']}): "
                f"Average = {row['average_marks']:.2f}%, Total = {row['total_marks']:.1f}, Grade = {row['grade']}"
            )

    print("\n Lowest Performer(s):")
    if lowest_df.empty:
        print("   No records available.")
    else:
        for _, row in lowest_df.iterrows():
            print(
                f"   * {row['student_name']} ({row['student_id']}, {row['department']}): "
                f"Average = {row['average_marks']:.2f}%, Total = {row['total_marks']:.1f}, Grade = {row['grade']}"
            )

    print(SECTION_DIVIDER + "\n")


def display_subject_averages(subject_averages: Dict[str, float]) -> None:
    """Display the class-wide average score for each subject.

    Parameters
    ----------
    subject_averages : Dict[str, float]
        Dictionary mapping subject names to average scores.
    """
    print(SECTION_DIVIDER)
    print(" 4. SUBJECT-WISE CLASS AVERAGES")
    print(SECTION_DIVIDER)

    friendly_names = {
        "math_marks": "Mathematics",
        "python_marks": "Python Programming",
        "data_science_marks": "Data Science",
    }

    print(f" {'Subject Name':<28} {'Class Average':>14}")
    print("-" * 45)
    for key, avg in subject_averages.items():
        name = friendly_names.get(key, key.replace("_", " ").title())
        print(f" {name:<28} {avg:>13.2f}%")

    print("-" * 45 + "\n")


def display_overall_average(overall_avg: float) -> None:
    """Display the aggregate overall class average.

    Parameters
    ----------
    overall_avg : float
        Overall aggregate average mark across the cohort.
    """
    print(SECTION_DIVIDER)
    print(" 5. OVERALL CLASS AVERAGE")
    print(SECTION_DIVIDER)
    print(f"  Aggregated Cohort Average Score : {overall_avg:.2f}%\n")


def display_pass_fail_summary(summary: Dict[str, Any]) -> None:
    """Display class pass/fail statistics and percentages.

    Parameters
    ----------
    summary : Dict[str, Any]
        Performance summary dictionary containing counts and percentages.
    """
    print(SECTION_DIVIDER)
    print(" 6. ACADEMIC OUTCOMES & PASS/FAIL DISTRIBUTION")
    print(SECTION_DIVIDER)

    total = summary.get("total_students", 0)
    passed = summary.get("passed_students", 0)
    pass_pct = summary.get("pass_percentage", 0.0)
    failed = summary.get("failed_students", 0)
    fail_pct = summary.get("fail_percentage", 0.0)

    print(f"  Total Enrolled Students : {total}")
    print(f"  Students Passed         : {passed:<5} ({pass_pct:.2f}%)")
    print(f"  Students Failed         : {failed:<5} ({fail_pct:.2f}%)")
    print(SECTION_DIVIDER + "\n")


def display_attendance_alerts(df: pd.DataFrame) -> None:
    """Display students with attendance below the mandatory threshold (75%).

    Parameters
    ----------
    df : pd.DataFrame
        Enriched student DataFrame.
    """
    print(SECTION_DIVIDER)
    print(" 7. ATTENDANCE SHORTAGE ADVISORY (< 75.0% ATTENDANCE)")
    print(SECTION_DIVIDER)

    shortage_students = df[df["attendance_pct"] < 75.0]

    if shortage_students.empty:
        print("  [Status: Healthy] All students meet the minimum 75% attendance threshold.")
    else:
        count = len(shortage_students)
        pct = (count / len(df)) * 100 if len(df) > 0 else 0.0
        print(f"  Total Flagged Students: {count} ({pct:.2f}% of cohort)\n")

        header = f"  {'ID':<8} {'Name':<20} {'Department':<24} {'Attendance':>10}"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for _, row in shortage_students.iterrows():
            print(
                f"  {str(row['student_id']):<8} "
                f"{str(row['student_name'])[:20]:<20} "
                f"{str(row['department'])[:24]:<24} "
                f"{row['attendance_pct']:>9.1f}%"
            )

    print(SECTION_DIVIDER + "\n")


def display_final_summary(summary: Dict[str, Any]) -> None:
    """Display a concise executive summary of the entire batch.

    Parameters
    ----------
    summary : Dict[str, Any]
        Performance summary dictionary.
    """
    print(DIVIDER_LINE)
    print(" 8. EXECUTIVE SUMMARY & KEY TAKEAWAYS")
    print(DIVIDER_LINE)
    print(f"  * Cohort Size           : {summary.get('total_students', 0)} students")
    print(f"  * Pass Rate             : {summary.get('pass_percentage', 0.0):.2f}% ({summary.get('passed_students', 0)} passed)")
    print(f"  * Fail Rate             : {summary.get('fail_percentage', 0.0):.2f}% ({summary.get('failed_students', 0)} failed)")
    print(f"  * Overall Class Average : {summary.get('overall_class_average', 0.0):.2f}%")
    print(f"  * Attendance Shortages  : {summary.get('attendance_shortage_students', 0)} students ({summary.get('attendance_shortage_percentage', 0.0):.2f}%)")
    print(DIVIDER_LINE + "\n")


def display_full_report(
    enriched_df: pd.DataFrame,
    summary: Dict[str, Any],
    top_performers: pd.DataFrame,
    highest_df: pd.DataFrame,
    lowest_df: pd.DataFrame,
) -> None:
    """Coordinate the display of all report sections in a structured order.

    Parameters
    ----------
    enriched_df : pd.DataFrame
        Complete enriched student dataset.
    summary : Dict[str, Any]
        Cohort statistical summary.
    top_performers : pd.DataFrame
        Top ranked students.
    highest_df : pd.DataFrame
        Highest performer(s).
    lowest_df : pd.DataFrame
        Lowest performer(s).
    """
    display_header()
    display_student_table(enriched_df)
    display_top_performers(top_performers)
    display_performance_extremes(highest_df, lowest_df)
    display_subject_averages(summary.get("subject_averages", {}))
    display_overall_average(summary.get("overall_class_average", 0.0))
    display_pass_fail_summary(summary)
    display_attendance_alerts(enriched_df)
    display_final_summary(summary)
