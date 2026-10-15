"""Unit tests for the Flask Backend API of Student Performance Analytics System.

Verifies that all API endpoints correctly integrate with the underlying
data_loader and analytics modules, returning accurate calculations and status codes.
"""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app


class TestBackendAPI(unittest.TestCase):
    """Test suite covering Flask REST API endpoints and data fidelity."""

    @classmethod
    def setUpClass(cls):
        """Set up test Flask client pointing to actual project dataset."""
        cls.app = create_app(PROJECT_ROOT / "data" / "students.csv")
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def test_api_health(self):
        """Verify /api/health returns 200 and healthy status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "healthy")
        self.assertEqual(json_data["total_records"], 26)

    def test_api_summary_metrics(self):
        """Verify /api/summary returns accurate cohort calculations from analytics.py."""
        response = self.client.get("/api/summary")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]

        # Expected values matching existing analytics.py calculations
        self.assertEqual(data["total_students"], 26)
        self.assertEqual(data["passed_count"], 22)
        self.assertEqual(data["failed_count"], 4)
        self.assertAlmostEqual(data["passed_pct"], 84.62, places=1)
        self.assertAlmostEqual(data["failed_pct"], 15.38, places=1)
        self.assertAlmostEqual(data["class_average"], 71.10, places=1)
        self.assertEqual(data["attendance_shortages_count"], 7)
        self.assertAlmostEqual(data["attendance_shortages_pct"], 26.92, places=1)

        # Top performers
        self.assertGreater(len(data["highest_performers"]), 0)
        self.assertEqual(data["highest_performers"][0]["student_id"], "STU104")

    def test_api_students_default_pagination(self):
        """Verify /api/students default returns 10 records per page and correct metadata."""
        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]

        self.assertEqual(data["total_records"], 26)
        self.assertEqual(data["filtered_records"], 26)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 10)
        self.assertEqual(len(data["students"]), 10)
        self.assertEqual(data["total_pages"], 3)
        self.assertIn("Computer Science", data["departments"])

    def test_api_students_department_filter(self):
        """Verify filtering by department returns only matching records."""
        response = self.client.get("/api/students?dept=Computer Science&page_size=50")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]

        self.assertGreater(data["filtered_records"], 0)
        for student in data["students"]:
            self.assertEqual(student["department"], "Computer Science")

    def test_api_students_search_query(self):
        """Verify search query by name or ID."""
        response = self.client.get("/api/students?search=Aarav")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]

        self.assertEqual(data["filtered_records"], 1)
        self.assertEqual(data["students"][0]["student_id"], "STU101")
        self.assertEqual(data["students"][0]["student_name"], "Aarav Sharma")

    def test_api_students_status_filter(self):
        """Verify filtering by passing status."""
        response = self.client.get("/api/students?status=fail&page_size=50")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]

        self.assertEqual(data["filtered_records"], 4)
        for s in data["students"]:
            self.assertEqual(s["passing_status"], "Fail")

    def test_api_analytics_payload(self):
        """Verify /api/analytics returns subject averages, charts data, and distributions."""
        response = self.client.get("/api/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]

        # Subject averages
        sub_avgs = data["subject_averages"]
        self.assertIn("Mathematics", sub_avgs)
        self.assertIn("Python Programming", sub_avgs)
        self.assertIn("Data Science", sub_avgs)
        self.assertAlmostEqual(sub_avgs["Mathematics"], 68.81, places=1)
        self.assertAlmostEqual(sub_avgs["Python Programming"], 72.73, places=1)
        self.assertAlmostEqual(sub_avgs["Data Science"], 71.77, places=1)

        # Grade distribution
        grades = [g["grade"] for g in data["grade_distribution"]]
        self.assertEqual(grades, ["A+", "A", "B", "C", "D", "E", "F"])

        # Top performers count
        self.assertEqual(len(data["top_performers"]), 3)

    def test_missing_csv_error_handling(self):
        """Verify clean error message without 500 crash when CSV does not exist."""
        bad_app = create_app(PROJECT_ROOT / "data" / "non_existent_file.csv")
        bad_client = bad_app.test_client()

        response = bad_client.get("/api/summary")
        self.assertEqual(response.status_code, 404)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "error")

    def test_index_page_serves_html(self):
        """Verify root URL / serves the frontend HTML dashboard."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Student Performance Analytics", response.data)
        self.assertIn(b"EduAnalytics", response.data)

    def test_static_assets_served(self):
        """Verify style.css and script.js are accessible from same origin."""
        css_res = self.client.get("/css/style.css")
        self.assertEqual(css_res.status_code, 200)
        self.assertIn(b":root", css_res.data)

        js_res = self.client.get("/js/script.js")
        self.assertEqual(js_res.status_code, 200)
        self.assertIn(b"DOMContentLoaded", js_res.data)

    def test_api_add_and_delete_student(self):
        """Verify adding a student and deleting the student works cleanly."""
        import tempfile
        import shutil
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            shutil.copyfile(PROJECT_ROOT / "data" / "students.csv", tmp_path)
            app = create_app(tmp_path)
            client = app.test_client()

            # Add student
            new_student = {
                "student_name": "Test Candidate",
                "department": "Computer Science",
                "math_marks": 80.0,
                "python_marks": 85.0,
                "data_science_marks": 90.0,
                "attendance_pct": 92.0
            }
            res = client.post("/api/students/add", json=new_student)
            self.assertEqual(res.status_code, 201)
            data = res.get_json()
            self.assertEqual(data["status"], "success")
            new_id = data["data"]["student_id"]
            self.assertEqual(data["data"]["student_name"], "Test Candidate")
            self.assertEqual(data["data"]["grade"], "A")

            # Delete student
            del_res = client.delete(f"/api/students/{new_id}")
            self.assertEqual(del_res.status_code, 200)
            del_data = del_res.get_json()
            self.assertEqual(del_data["status"], "success")
            self.assertEqual(del_data["deleted_id"], new_id)

            # Deleting again should return 404
            del_404 = client.delete(f"/api/students/{new_id}")
            self.assertEqual(del_404.status_code, 404)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()

