"""Main orchestrator for Student Performance Analytics System.

Coordinates dataset loading, validation, analytical metric calculations,
and formatted terminal reporting.
"""

import sys
from pathlib import Path

# Ensure project root is present in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.data_loader import load_data, clean_data
    from src.analytics import (
        enrich_student_dataset,
        get_performance_summary,
        get_top_students,
        get_performance_extremes,
    )
    from src.display import display_full_report
except ImportError as err:
    print(f"\n[Fatal Error] Failed to import required application modules: {err}")
    print("Please verify that all project dependencies in 'requirements.txt' are installed.")
    sys.exit(1)


def run_pipeline(csv_path: Path = None) -> int:
    """Execute the end-to-end student analytics pipeline.

    Parameters
    ----------
    csv_path : Path, optional
        Path to the students CSV dataset. If not provided, defaults
        to 'data/students.csv' relative to this script.

    Returns
    -------
    int
        Exit code: 0 for success, 1 for errors.
    """
    if csv_path is None:
        csv_path = PROJECT_ROOT / "data" / "students.csv"

    try:
        # Step 1: Ingest raw dataset
        raw_df = load_data(csv_path)

        # Step 2: Clean and validate dataset
        clean_df = clean_data(raw_df)

        # Step 3: Run analytics computations
        enriched_df = enrich_student_dataset(clean_df)
        summary = get_performance_summary(enriched_df)
        top_performers = get_top_students(enriched_df, n=3)
        highest_df, lowest_df = get_performance_extremes(enriched_df)

        # Step 4: Display terminal report
        display_full_report(
            enriched_df=enriched_df,
            summary=summary,
            top_performers=top_performers,
            highest_df=highest_df,
            lowest_df=lowest_df,
        )

        print("[Success] Student Performance Analytics pipeline executed successfully.\n")
        return 0

    except FileNotFoundError as fnf_err:
        print(f"\n[Error: Missing File] {fnf_err}")
        print("Please check that the CSV dataset exists at the expected path.")
        return 1
    except ValueError as val_err:
        print(f"\n[Error: Data Validation Failure] {val_err}")
        print("Please review dataset contents for formatting or schema issues.")
        return 1
    except TypeError as type_err:
        print(f"\n[Error: Type Error] {type_err}")
        return 1
    except Exception as exc:
        print(f"\n[Unexpected Error] An unexpected error occurred: {exc}")
        return 1


def add_student_cli(csv_path: Path = None) -> bool:
    """Interactively collect details and add a new student record to CSV."""
    import pandas as pd
    if csv_path is None:
        csv_path = PROJECT_ROOT / "data" / "students.csv"

    print("\n------------------------------------------------------")
    print("  ADD NEW STUDENT RECORD")
    print("------------------------------------------------------")

    name = input("Enter Student Name: ").strip()
    if not name:
        print("[Error] Student name cannot be empty.")
        return False

    departments = [
        "Computer Science",
        "Artificial Intelligence",
        "Information Technology",
        "Data Science",
    ]
    print("\nSelect Department:")
    for i, dept in enumerate(departments, 1):
        print(f"  [{i}] {dept}")

    try:
        dept_choice = int(input("Enter department choice (1-4): ").strip())
        if not (1 <= dept_choice <= len(departments)):
            print("[Error] Invalid choice.")
            return False
        selected_dept = departments[dept_choice - 1]
    except ValueError:
        print("[Error] Please enter a valid number (1-4).")
        return False

    def get_float_input(prompt: str) -> float:
        val = float(input(prompt).strip())
        if val < 0 or val > 100:
            raise ValueError("Marks/Attendance must be between 0 and 100.")
        return round(val, 2)

    try:
        math = get_float_input("Enter Mathematics Marks (0-100): ")
        python_m = get_float_input("Enter Python Marks (0-100): ")
        ds_m = get_float_input("Enter Data Science Marks (0-100): ")
        att = get_float_input("Enter Attendance Percentage (0-100): ")
    except ValueError as val_err:
        print(f"[Error] {val_err}")
        return False

    raw_df = load_data(csv_path)
    clean_df = clean_data(raw_df)

    # Next student ID
    existing_nums = []
    for sid in clean_df["student_id"]:
        try:
            existing_nums.append(int(str(sid).replace("STU", "")))
        except ValueError:
            continue
    next_id = f"STU{max(existing_nums) + 1 if existing_nums else 101}"

    new_row = pd.DataFrame([{
        "student_id": next_id,
        "student_name": name,
        "department": selected_dept,
        "math_marks": math,
        "python_marks": python_m,
        "data_science_marks": ds_m,
        "attendance_pct": att,
    }])

    updated_df = pd.concat([clean_df, new_row], ignore_index=True)
    raw_cols = [
        "student_id", "student_name", "department",
        "math_marks", "python_marks", "data_science_marks", "attendance_pct"
    ]
    updated_df[raw_cols].to_csv(csv_path, index=False)
    print(f"\n[Success] Student '{name}' successfully added with ID: {next_id}!\n")
    return True


def delete_student_cli(csv_path: Path = None) -> bool:
    """Interactively delete a student record by student_id from CSV."""
    if csv_path is None:
        csv_path = PROJECT_ROOT / "data" / "students.csv"

    print("\n------------------------------------------------------")
    print("  DELETE STUDENT RECORD")
    print("------------------------------------------------------")

    raw_df = load_data(csv_path)
    clean_df = clean_data(raw_df)

    target_id = input("Enter Student ID to delete (e.g. STU101): ").strip().upper()
    match = clean_df[clean_df["student_id"] == target_id]

    if match.empty:
        print(f"[Error] Student ID '{target_id}' not found in records.")
        return False

    target_name = match.iloc[0]["student_name"]
    target_dept = match.iloc[0]["department"]
    confirm = input(f"Are you sure you want to delete '{target_name}' ({target_id}, {target_dept})? (y/N): ").strip().lower()

    if confirm != "y":
        print("[Cancelled] Deletion cancelled by user.")
        return False

    updated_df = clean_df[clean_df["student_id"] != target_id].reset_index(drop=True)
    raw_cols = [
        "student_id", "student_name", "department",
        "math_marks", "python_marks", "data_science_marks", "attendance_pct"
    ]
    updated_df[raw_cols].to_csv(csv_path, index=False)
    print(f"\n[Success] Student '{target_name}' ({target_id}) deleted successfully!\n")
    return True


def main() -> None:
    """Main CLI entry point with interactive menu support."""
    # Run pipeline directly if --report flag given or if non-interactive environment
    if "--report" in sys.argv or not sys.stdin.isatty():
        exit_code = run_pipeline()
        sys.exit(exit_code)

    while True:
        print("\n=======================================================")
        print("  Student Performance Analytics System - CLI Menu")
        print("=======================================================")
        print("  [1] View Full Analytics Report")
        print("  [2] Add New Student")
        print("  [3] Delete Student")
        print("  [4] Start Web Dashboard Server (http://127.0.0.1:5000)")
        print("  [5] Exit")
        print("=======================================================")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            run_pipeline()
        elif choice == "2":
            add_student_cli()
        elif choice == "3":
            delete_student_cli()
        elif choice == "4":
            print("\nStarting Web Server on http://127.0.0.1:5000 ... (Press Ctrl+C to stop)")
            from backend.app import app
            app.run(host="127.0.0.1", port=5000, debug=False)
        elif choice == "5" or choice.lower() in ("q", "quit", "exit"):
            print("\nGoodbye!\n")
            sys.exit(0)
        else:
            print("[Warning] Invalid choice. Please select 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()

