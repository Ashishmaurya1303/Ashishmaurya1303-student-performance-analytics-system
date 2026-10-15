"""Flask Backend API for Student Performance Analytics System.

Connects the existing Python, Pandas, and NumPy analytics pipeline to the web dashboard,
serving both JSON REST API endpoints and static frontend assets from the same origin.
"""

import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Optional
from flask import Flask, jsonify, request, send_from_directory

# Dynamic path resolution ensuring imports work from any working directory
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import existing core modules without modifying or duplicating analytics logic
from src.data_loader import load_data, clean_data
from src.analytics import (
    enrich_student_dataset,
    get_performance_summary,
    get_top_students,
    get_performance_extremes,
    calculate_subject_averages,
    calculate_overall_average,
)


def _resolve_writable_csv_path(base_csv: Path) -> Path:
    """Resolve a guaranteed-writable CSV path, adapting to Vercel/serverless environments."""
    is_serverless = bool(
        os.environ.get("VERCEL")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        or os.environ.get("VERCEL_ENV")
    )
    if is_serverless:
        tmp_csv = Path(tempfile.gettempdir()) / "students.csv"
        if not tmp_csv.exists() and base_csv.exists():
            try:
                shutil.copyfile(base_csv, tmp_csv)
            except Exception:
                pass
        return tmp_csv if tmp_csv.exists() else base_csv

    # On local systems, test if base_csv is writable
    try:
        if base_csv.exists():
            with open(base_csv, "a"):
                pass
        return base_csv
    except (OSError, PermissionError):
        tmp_csv = Path(tempfile.gettempdir()) / "students.csv"
        if not tmp_csv.exists() and base_csv.exists():
            try:
                shutil.copyfile(base_csv, tmp_csv)
            except Exception:
                pass
        return tmp_csv if tmp_csv.exists() else base_csv


def create_app(custom_csv_path: Optional[Path] = None) -> Flask:
    """Application factory for Flask analytics API."""
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="",
    )

    # Dataset path resolution with serverless write-support
    default_csv = PROJECT_ROOT / "data" / "students.csv"
    app.config["DEFAULT_CSV_PATH"] = default_csv
    app.config["CSV_PATH"] = custom_csv_path or _resolve_writable_csv_path(default_csv)

    def get_processed_data():
        """Load, clean, and enrich dataset using existing Python logic."""
        csv_path = Path(app.config["CSV_PATH"])
        if not csv_path.exists():
            default_csv = Path(app.config.get("DEFAULT_CSV_PATH", PROJECT_ROOT / "data" / "students.csv"))
            if default_csv.exists():
                try:
                    shutil.copyfile(default_csv, csv_path)
                except Exception:
                    csv_path = default_csv
            else:
                raise FileNotFoundError(f"Dataset CSV file not found at '{csv_path.name}'.")
        raw_df = load_data(csv_path)
        clean_df = clean_data(raw_df)
        enriched_df = enrich_student_dataset(clean_df)
        return enriched_df

    # -------------------------------------------------------------
    # Static UI Routes (Same Origin)
    # -------------------------------------------------------------
    @app.route("/")
    def index():
        """Serve the dashboard homepage."""
        return send_from_directory(FRONTEND_DIR, "index.html")

    # -------------------------------------------------------------
    # API Routes
    # -------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def api_health():
        """Health check endpoint validating data pipeline integrity."""
        try:
            df = get_processed_data()
            return jsonify({
                "status": "healthy",
                "message": "Student Performance Analytics System API is running smoothly.",
                "total_records": int(len(df)),
            }), 200
        except FileNotFoundError as fnf_err:
            return jsonify({
                "status": "error",
                "error_type": "FileNotFoundError",
                "message": str(fnf_err),
            }), 404
        except ValueError as val_err:
            return jsonify({
                "status": "error",
                "error_type": "ValidationError",
                "message": str(val_err),
            }), 400
        except Exception:
            return jsonify({
                "status": "error",
                "error_type": "ServerException",
                "message": "An unexpected error occurred while loading the dataset.",
            }), 500

    @app.route("/api/summary", methods=["GET"])
    def api_summary():
        """Get high-level cohort executive summary metrics."""
        try:
            df = get_processed_data()
            summary = get_performance_summary(df)
            highest_df, lowest_df = get_performance_extremes(df)

            # Format extremes for clean JSON serialization
            highest_list = highest_df[[
                "student_id", "student_name", "department", "total_marks", "average_marks", "grade"
            ]].to_dict(orient="records")

            lowest_list = lowest_df[[
                "student_id", "student_name", "department", "total_marks", "average_marks", "grade"
            ]].to_dict(orient="records")

            return jsonify({
                "status": "success",
                "data": {
                    "total_students": summary["total_students"],
                    "passed_count": summary["passed_students"],
                    "passed_pct": summary["pass_percentage"],
                    "failed_count": summary["failed_students"],
                    "failed_pct": summary["fail_percentage"],
                    "class_average": summary["overall_class_average"],
                    "attendance_shortages_count": summary["attendance_shortage_students"],
                    "attendance_shortages_pct": summary["attendance_shortage_percentage"],
                    "highest_performers": highest_list,
                    "lowest_performers": lowest_list,
                }
            }), 200

        except FileNotFoundError as fnf_err:
            return jsonify({"status": "error", "message": str(fnf_err)}), 404
        except ValueError as val_err:
            return jsonify({"status": "error", "message": str(val_err)}), 400
        except Exception:
            return jsonify({"status": "error", "message": "Failed to compute summary statistics."}), 500

    @app.route("/api/students", methods=["GET"])
    def api_students():
        """Get student records with search, department filtering, sorting, and pagination."""
        try:
            df = get_processed_data()
            total_records = len(df)

            # Distinct departments for frontend filter dropdown
            departments = sorted(df["department"].dropna().unique().tolist())

            # 1. Department filter
            dept = request.args.get("dept", "").strip()
            if dept and dept.lower() != "all":
                df = df[df["department"].str.lower() == dept.lower()]

            # 2. Status filter (pass, fail, shortage)
            status_filter = request.args.get("status", "").strip().lower()
            if status_filter == "pass":
                df = df[df["status"] == "Pass"]
            elif status_filter == "fail":
                df = df[df["status"] == "Fail"]
            elif status_filter == "shortage":
                df = df[df["attendance_status"] == "Shortage"]

            # 3. Search filter (by student_id or student_name)
            search_query = request.args.get("search", "").strip()
            if search_query:
                mask = (
                    df["student_id"].str.contains(search_query, case=False, na=False) |
                    df["student_name"].str.contains(search_query, case=False, na=False)
                )
                df = df[mask]

            filtered_records = len(df)

            # 4. Sorting
            sort_by = request.args.get("sort_by", "student_id").strip()
            order = request.args.get("order", "asc").strip().lower()
            ascending = order != "desc"

            valid_sort_columns = [
                "student_id", "student_name", "department", "math_marks",
                "python_marks", "data_science_marks", "total_marks",
                "average_marks", "grade", "status", "attendance_pct"
            ]
            if sort_by in valid_sort_columns and not df.empty:
                df = df.sort_values(by=sort_by, ascending=ascending)

            # 5. Pagination
            try:
                page = max(1, int(request.args.get("page", 1)))
            except ValueError:
                page = 1

            try:
                page_size = int(request.args.get("page_size", 10))
            except ValueError:
                page_size = 10

            if page_size > 0:
                total_pages = max(1, (filtered_records + page_size - 1) // page_size)
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                paged_df = df.iloc[start_idx:end_idx]
            else:
                total_pages = 1
                paged_df = df

            # Prepare records with status and passing_status alias
            records = paged_df.to_dict(orient="records")
            for r in records:
                r["passing_status"] = r.get("status", "")

            return jsonify({
                "status": "success",
                "data": {
                    "students": records,
                    "total_records": total_records,
                    "filtered_records": filtered_records,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "departments": departments,
                }
            }), 200

        except FileNotFoundError as fnf_err:
            return jsonify({"status": "error", "message": str(fnf_err)}), 404
        except ValueError as val_err:
            return jsonify({"status": "error", "message": str(val_err)}), 400
        except Exception:
            return jsonify({"status": "error", "message": "Failed to retrieve student records."}), 500

    @app.route("/api/analytics", methods=["GET"])
    def api_analytics():
        """Get structured academic analytics data for Chart.js and statistical breakdowns."""
        try:
            df = get_processed_data()

            # Subject averages using existing analytics function
            raw_subject_avgs = calculate_subject_averages(df)
            subject_name_map = {
                "math_marks": "Mathematics",
                "python_marks": "Python Programming",
                "data_science_marks": "Data Science",
            }
            subject_avgs = {
                subject_name_map.get(k, k): v for k, v in raw_subject_avgs.items()
            }

            # Pass/fail counts using existing calculations
            passed_cnt = int((df["status"] == "Pass").sum())
            failed_cnt = int((df["status"] == "Fail").sum())
            total_cnt = len(df)
            pass_fail = {
                "total": total_cnt,
                "passed": passed_cnt,
                "failed": failed_cnt,
                "pass_pct": round((passed_cnt / total_cnt) * 100.0, 2),
                "fail_pct": round((failed_cnt / total_cnt) * 100.0, 2),
            }

            # Top 3 students using existing analytics function
            top_students = get_top_students(df, n=3).to_dict(orient="records")

            # Attendance shortages using existing analytics logic
            shortages_df = df[df["attendance_status"] == "Shortage"]
            shortages = shortages_df[[
                "student_id", "student_name", "department", "attendance_pct"
            ]].to_dict(orient="records")

            # Department comparison (average marks, count, pass rate)
            dept_grouped = df.groupby("department").agg(
                student_count=("student_id", "count"),
                avg_math=("math_marks", "mean"),
                avg_python=("python_marks", "mean"),
                avg_ds=("data_science_marks", "mean"),
                overall_avg=("average_marks", "mean"),
                passed_count=("status", lambda s: (s == "Pass").sum()),
            ).reset_index()

            dept_grouped["pass_rate"] = (
                (dept_grouped["passed_count"] / dept_grouped["student_count"]) * 100.0
            ).round(2)
            dept_grouped["overall_avg"] = dept_grouped["overall_avg"].round(2)
            dept_grouped["avg_math"] = dept_grouped["avg_math"].round(2)
            dept_grouped["avg_python"] = dept_grouped["avg_python"].round(2)
            dept_grouped["avg_ds"] = dept_grouped["avg_ds"].round(2)

            dept_comparison = dept_grouped.to_dict(orient="records")

            # Grade distribution
            grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
            grade_counts_series = df["grade"].value_counts()
            grade_distribution = [
                {"grade": g, "count": int(grade_counts_series.get(g, 0))}
                for g in grade_order
            ]

            return jsonify({
                "status": "success",
                "data": {
                    "subject_averages": subject_avgs,
                    "pass_fail": pass_fail,
                    "department_comparison": dept_comparison,
                    "grade_distribution": grade_distribution,
                    "top_performers": top_students,
                    "attendance_shortages": shortages,
                }
            }), 200

        except FileNotFoundError as fnf_err:
            return jsonify({"status": "error", "message": str(fnf_err)}), 404
        except ValueError as val_err:
            return jsonify({"status": "error", "message": str(val_err)}), 400
        except Exception:
            return jsonify({"status": "error", "message": "Failed to compute analytics charts data."}), 500

    # -----------------------------------------------------------------
    # CRUD Routes: Add Student & Delete Student
    # -----------------------------------------------------------------

    def _save_raw_dataframe_to_csv(raw_df: 'pd.DataFrame') -> None:
        """Persist the raw DataFrame back to CSV with serverless read-only fallback."""
        csv_path = Path(app.config["CSV_PATH"])
        raw_columns = [
            "student_id", "student_name", "department",
            "math_marks", "python_marks", "data_science_marks", "attendance_pct"
        ]
        save_df = raw_df[raw_columns].copy()
        try:
            save_df.to_csv(csv_path, index=False)
        except (OSError, PermissionError):
            # Fallback for Vercel/AWS Lambda read-only filesystem
            tmp_csv = Path(tempfile.gettempdir()) / "students.csv"
            save_df.to_csv(tmp_csv, index=False)
            app.config["CSV_PATH"] = tmp_csv

    def _get_raw_dataframe() -> 'pd.DataFrame':
        """Load and clean the dataset (without enrichment) for modification."""
        csv_path = Path(app.config["CSV_PATH"])
        if not csv_path.exists():
            default_csv = Path(app.config.get("DEFAULT_CSV_PATH", PROJECT_ROOT / "data" / "students.csv"))
            if default_csv.exists():
                try:
                    shutil.copyfile(default_csv, csv_path)
                except Exception:
                    csv_path = default_csv
            else:
                raise FileNotFoundError(f"Dataset CSV file not found at '{csv_path.name}'.")
        raw_df = load_data(csv_path)
        cleaned_df = clean_data(raw_df)
        return cleaned_df

    def _generate_next_student_id(df: 'pd.DataFrame') -> str:
        """Generate the next STU### student ID by finding the highest existing number."""
        if df.empty:
            return "STU101"
        existing_nums = []
        for sid in df["student_id"]:
            try:
                num_part = int(str(sid).replace("STU", ""))
                existing_nums.append(num_part)
            except ValueError:
                continue
        next_num = max(existing_nums) + 1 if existing_nums else 101
        return f"STU{next_num}"

    @app.route("/api/students/add", methods=["POST"])
    def api_add_student():
        """Add a new student record to the dataset.

        Expects JSON body with fields:
        - student_name (required, string)
        - department (required, one of: Computer Science, Artificial Intelligence,
                      Information Technology, Data Science)
        - math_marks (required, float 0-100)
        - python_marks (required, float 0-100)
        - data_science_marks (required, float 0-100)
        - attendance_pct (required, float 0-100)
        """
        try:
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({"status": "error", "message": "Request body must be valid JSON."}), 400

            # Validate required fields
            required_fields = [
                "student_name", "department", "math_marks",
                "python_marks", "data_science_marks", "attendance_pct"
            ]
            missing = [f for f in required_fields if f not in data or data[f] is None]
            if missing:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {missing}"
                }), 400

            # Validate student name
            name = str(data["student_name"]).strip()
            if not name or name.lower() in ("nan", "none", ""):
                return jsonify({"status": "error", "message": "Student name cannot be empty."}), 400

            # Validate department
            valid_departments = [
                "Computer Science", "Artificial Intelligence",
                "Information Technology", "Data Science"
            ]
            department = str(data["department"]).strip()
            if department not in valid_departments:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid department. Must be one of: {valid_departments}"
                }), 400

            # Validate numeric fields (0-100)
            numeric_fields = ["math_marks", "python_marks", "data_science_marks", "attendance_pct"]
            parsed_nums = {}
            for field in numeric_fields:
                try:
                    val = float(data[field])
                    if val < 0 or val > 100:
                        return jsonify({
                            "status": "error",
                            "message": f"'{field}' must be between 0 and 100. Got: {val}"
                        }), 400
                    parsed_nums[field] = round(val, 2)
                except (ValueError, TypeError):
                    return jsonify({
                        "status": "error",
                        "message": f"'{field}' must be a valid number. Got: {data[field]}"
                    }), 400

            # Load current dataset, generate ID, and append
            cleaned_df = _get_raw_dataframe()
            new_id = _generate_next_student_id(cleaned_df)

            import pandas as pd
            new_row = pd.DataFrame([{
                "student_id": new_id,
                "student_name": name,
                "department": department,
                "math_marks": parsed_nums["math_marks"],
                "python_marks": parsed_nums["python_marks"],
                "data_science_marks": parsed_nums["data_science_marks"],
                "attendance_pct": parsed_nums["attendance_pct"],
            }])

            updated_df = pd.concat([cleaned_df, new_row], ignore_index=True)

            # Save raw data back to CSV
            _save_raw_dataframe_to_csv(updated_df)

            # Re-enrich to return the complete student record
            enriched_df = enrich_student_dataset(updated_df)
            added_student = enriched_df[enriched_df["student_id"] == new_id].to_dict(orient="records")

            return jsonify({
                "status": "success",
                "message": f"Student '{name}' added successfully with ID {new_id}.",
                "data": added_student[0] if added_student else {}
            }), 201

        except FileNotFoundError as fnf_err:
            return jsonify({"status": "error", "message": str(fnf_err)}), 404
        except ValueError as val_err:
            return jsonify({"status": "error", "message": str(val_err)}), 400
        except Exception as exc:
            return jsonify({"status": "error", "message": f"Failed to add student: {str(exc)}"}), 500

    @app.route("/api/students/<string:student_id>", methods=["DELETE"])
    def api_delete_student(student_id: str):
        """Delete a student record from the dataset by student_id.

        Parameters
        ----------
        student_id : str
            The unique student ID to delete (e.g., 'STU101').
        """
        try:
            student_id = student_id.strip()
            if not student_id:
                return jsonify({"status": "error", "message": "Student ID cannot be empty."}), 400

            cleaned_df = _get_raw_dataframe()

            # Check if student exists
            match = cleaned_df[cleaned_df["student_id"] == student_id]
            if match.empty:
                return jsonify({
                    "status": "error",
                    "message": f"Student with ID '{student_id}' not found in dataset."
                }), 404

            student_name = match.iloc[0]["student_name"]

            # Remove the student
            updated_df = cleaned_df[cleaned_df["student_id"] != student_id].reset_index(drop=True)

            # Save back to CSV
            _save_raw_dataframe_to_csv(updated_df)

            return jsonify({
                "status": "success",
                "message": f"Student '{student_name}' ({student_id}) deleted successfully.",
                "deleted_id": student_id,
                "deleted_name": student_name,
            }), 200

        except FileNotFoundError as fnf_err:
            return jsonify({"status": "error", "message": str(fnf_err)}), 404
        except ValueError as val_err:
            return jsonify({"status": "error", "message": str(val_err)}), 400
        except Exception as exc:
            return jsonify({"status": "error", "message": f"Failed to delete student: {str(exc)}"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    print("\n=======================================================")
    print("  Student Performance Analytics System - Web Server")
    print("  Serving frontend & API at: http://127.0.0.1:5000")
    print("=======================================================\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
