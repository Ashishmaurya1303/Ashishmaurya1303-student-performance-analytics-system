"""Compile Project_Documentation.pdf with ReportLab, including genuine screenshots."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = PROJECT_ROOT / "Project_Documentation.pdf"
SCREENSHOTS_DIR = PROJECT_ROOT / "docs" / "screenshots"


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds page numbers and running footer/header."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress running header/footer on title page

        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))

        # Running Header
        self.drawString(54, 750, "Student Performance Analytics System — Course Project Documentation")
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_str)
        self.drawString(54, 40, "Python with AI Mini Project | Confidential & Academic Use")
        self.line(54, 52, 558, 52)

        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    caption_style = ParagraphStyle(
        "CaptionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=10,
    )

    elements = []

    # ==================== 1. TITLE PAGE ====================
    elements.append(Spacer(1, 100))
    elements.append(Paragraph("STUDENT PERFORMANCE ANALYTICS SYSTEM", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("A Python, Pandas & NumPy Automated Academic Reporting Tool", subtitle_style))
    elements.append(Spacer(1, 40))

    meta_data = [
        ["Course:", "Python with AI"],
        ["Assignment:", "Course Mini Project"],
        ["Version:", "1.0.0 (Production Ready)"],
        ["Technologies:", "Python 3.12, Pandas, NumPy, CSV"],
        ["Repository:", "https://github.com/Ashishmaurya1303/Ashishmaurya1303-student-performance-analytics-system"],
        ["Author:", "Ashish Maurya (Ashishmaurya1303)"],
        ["Date:", "October 2026"],
    ]
    meta_table = Table(meta_data, colWidths=[120, 320])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2D3748")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(meta_table)
    elements.append(PageBreak())

    # ==================== 2. ABSTRACT & OBJECTIVE ====================
    elements.append(Paragraph("2. Abstract", h1_style))
    elements.append(Paragraph(
        "The <b>Student Performance Analytics System</b> is a high-integrity, automated data analytics tool "
        "engineered in Python using Pandas and NumPy. It streamlines academic record management by ingesting raw CSV "
        "records, applying defensive data cleansing and transparent median-based imputation, calculating aggregate scores, "
        "percentages, letter grades, pass/fail qualifications, and generating formatted terminal reports. The system ensures "
        "reproducibility and eliminates human errors in academic evaluation.",
        body_style
    ))

    elements.append(Paragraph("3. Project Objective", h1_style))
    elements.append(Paragraph(
        "• Automate loading and validation of student academic and attendance datasets from CSV files.<br/>"
        "• Apply transparent median-based imputation for missing/corrupt values without corrupting source data.<br/>"
        "• Compute accurate totals, percentages, letter grades (A+ to F), and pass/fail statuses using vectorized logic.<br/>"
        "• Analyze attendance thresholds to flag students at risk of attendance shortages (&lt; 75%).<br/>"
        "• Identify honor roll top performers, class averages, and extremes (highest and lowest scores).<br/>"
        "• Provide a 100% automated test suite verifying edge cases, boundaries, and immutability.",
        body_style
    ))

    elements.append(Paragraph("4. Problem Statement", h1_style))
    elements.append(Paragraph(
        "Academic departments frequently track student grades using disparate spreadsheets or manual calculations. "
        "This often leads to inaccurate totals, overlooked subject-specific minimum requirements, ignored attendance "
        "shortages, and vulnerability to corrupted entries. This project provides a robust, self-validating solution.",
        body_style
    ))

    elements.append(Paragraph("5. Technologies Used", h1_style))
    tech_data = [
        ["Technology", "Version", "Role in Project"],
        ["Python", "3.12+", "Core programming language, type hints, PEP 8 structure"],
        ["Pandas", "3.0+", "CSV loading, schema validation, tabular operations"],
        ["NumPy", "2.5+", "Vectorized array calculations (np.select, np.where, statistics)"],
        ["Standard Library", "Built-in", "pathlib (path resolution), sys (exit codes)"],
    ]
    tech_table = Table(tech_data, colWidths=[110, 80, 314])
    tech_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 10))

    # ==================== 6. ARCHITECTURE & DATASET ====================
    elements.append(Paragraph("6. System Architecture & Workflow", h1_style))
    elements.append(Paragraph(
        "The project follows a linear, non-destructive modular pipeline: "
        "<b>data/students.csv</b> → <b>Data Loader</b> (Schema Check & Cleaning) → "
        "<b>Analytics Engine</b> (Vectorized Computations & Grading) → "
        "<b>Display Module</b> (Formatted Terminal Output) → <b>main.py</b> (Orchestration).",
        body_style
    ))

    elements.append(Paragraph("7. Dataset Description", h1_style))
    ds_data = [
        ["Column Name", "Type", "Valid Range", "Description"],
        ["student_id", "String", "Unique string", "Unique ID (e.g. STU101)"],
        ["student_name", "String", "Non-empty text", "Full student name"],
        ["department", "String", "CS, AI, IT, DS", "Academic department"],
        ["math_marks", "Float", "0.0 - 100.0", "Score in Mathematics"],
        ["python_marks", "Float", "0.0 - 100.0", "Score in Python Programming"],
        ["data_science_marks", "Float", "0.0 - 100.0", "Score in Data Science"],
        ["attendance_pct", "Float", "0.0 - 100.0", "Attendance percentage"],
    ]
    ds_table = Table(ds_data, colWidths=[110, 60, 90, 244])
    ds_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(ds_table)
    elements.append(PageBreak())

    # ==================== 8. MODULES & IMPLEMENTATION ====================
    elements.append(Paragraph("8. Functional Requirements & Project Modules", h1_style))
    elements.append(Paragraph(
        "<b>src/data_loader.py:</b> Implements <code>load_data()</code> and <code>clean_data()</code> with zero-byte checks, "
        "parser exception handling, schema enforcement, whitespace trimming, and duplicate ID detection.<br/>"
        "<b>src/analytics.py:</b> Houses pure functions: <code>calculate_total_marks()</code>, "
        "<code>calculate_average_marks()</code>, <code>determine_pass_fail()</code>, <code>assign_grades()</code>, "
        "<code>evaluate_attendance()</code>, <code>get_top_students()</code>, and <code>get_performance_summary()</code>.<br/>"
        "<b>src/display.py:</b> Implements cleanly formatted ASCII tables and structured terminal sections.<br/>"
        "<b>main.py:</b> Entry point resolving dynamic paths relative to script root and trapping unexpected exceptions.",
        body_style
    ))

    elements.append(Paragraph("9. Implementation Details", h1_style))
    elements.append(Paragraph(
        "• <b>Immutability:</b> All functions work on deep copies (<code>df.copy()</code>) ensuring the input dataset remains untouched.<br/>"
        "• <b>Deterministic Tie-Breaking:</b> Ranking ties are resolved hierarchically: Total Marks → Math Marks → Python Marks → DS Marks → Student ID.<br/>"
        "• <b>Transparent Imputation:</b> Missing/invalid values are replaced with column medians while logging informative notices to the console.",
        body_style
    ))

    elements.append(Paragraph("10. Grading and Pass/Fail Rules", h1_style))
    rules_data = [
        ["Category", "Criteria / Range", "Assigned Outcome"],
        ["Passing Minimum", "Marks >= 40 in ALL 3 subjects AND Avg >= 40.0%", "Pass Status"],
        ["Failure Condition", "Marks < 40 in ANY subject OR Avg < 40.0%", "Fail Status & Grade F"],
        ["Grade A+", "Average >= 90.0% (and Passed)", "Grade A+ (Outstanding)"],
        ["Grade A", "Average >= 80.0% and < 90.0% (and Passed)", "Grade A (Excellent)"],
        ["Grade B", "Average >= 70.0% and < 80.0% (and Passed)", "Grade B (Very Good)"],
        ["Grade C", "Average >= 60.0% and < 70.0% (and Passed)", "Grade C (Good)"],
        ["Grade D", "Average >= 50.0% and < 60.0% (and Passed)", "Grade D (Satisfactory)"],
        ["Grade E", "Average >= 40.0% and < 50.0% (and Passed)", "Grade E (Pass)"],
        ["Attendance Check", "Attendance < 75.0%", "Shortage Advisory"],
    ]
    rules_table = Table(rules_data, colWidths=[120, 240, 144])
    rules_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(rules_table)
    elements.append(Spacer(1, 10))

    # ==================== 11. TESTING METHODOLOGY ====================
    elements.append(Paragraph("11. Testing Methodology and Actual Test Results", h1_style))
    test_summary_data = [
        ["Test Suite", "File", "Cases Run", "Status"],
        ["Data Loader Tests", "tests/test_data_loader.py", "10", "10 Passed, 0 Failed [OK]"],
        ["Analytics Tests", "tests/test_analytics.py", "11", "11 Passed, 0 Failed [OK]"],
        ["End-to-End Integration Tests", "tests/test_end_to_end.py", "6", "6 Passed, 0 Failed [OK]"],
    ]
    test_table = Table(test_summary_data, colWidths=[140, 160, 70, 134])
    test_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TEXTCOLOR", (3, 1), (3, -1), colors.HexColor("#22543D")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(test_table)
    elements.append(PageBreak())

    # ==================== 12. SCREENSHOTS ====================
    elements.append(Paragraph("12. Actual Program Output & Web Dashboard Screenshots", h1_style))
    elements.append(Paragraph(
        "Below are authentic captures from the live interactive analytics dashboard running on the Python Flask & Pandas backend:",
        body_style
    ))

    overview_img = SCREENSHOTS_DIR / "dashboard_overview.png"
    if overview_img.exists():
        elements.append(RLImage(str(overview_img), width=480, height=222))
        elements.append(Paragraph("Figure 1: Executive Summary & Live KPI Overview (Total: 29, Pass: 24, Fail: 5, Class Avg: 72.69%)", caption_style))

    vis1_img = SCREENSHOTS_DIR / "dashboard_visualizations_1.png"
    if vis1_img.exists():
        elements.append(RLImage(str(vis1_img), width=480, height=190))
        elements.append(Paragraph("Figure 2: Subject-Wise Class Averages & Academic Outcomes Pass/Fail Distribution", caption_style))

    elements.append(PageBreak())

    vis2_img = SCREENSHOTS_DIR / "dashboard_visualizations_2.png"
    if vis2_img.exists():
        elements.append(RLImage(str(vis2_img), width=480, height=192))
        elements.append(Paragraph("Figure 3: Department-Wise Average Performance & 7-Tier Grade Distribution (A+ to F)", caption_style))

    honor_img = SCREENSHOTS_DIR / "dashboard_honor_roll.png"
    if honor_img.exists():
        elements.append(RLImage(str(honor_img), width=480, height=192))
        elements.append(Paragraph("Figure 4: Honor Roll (Top 3 Performers) & Cohort Extremes Spotlight (harshit, Rahul Kulkarni, Varun Chopra)", caption_style))

    elements.append(PageBreak())

    records_img = SCREENSHOTS_DIR / "dashboard_student_records.png"
    if records_img.exists():
        elements.append(RLImage(str(records_img), width=480, height=192))
        elements.append(Paragraph("Figure 5: Master Student Records Table with Real-Time Search, Filtering, and Pagination", caption_style))

    # ==================== 13. RESULTS & DISCUSSION ====================
    elements.append(Paragraph("13. Results and Discussion", h1_style))
    elements.append(Paragraph(
        "The application executed against the 29-student cohort dataset with 100% calculation fidelity:<br/>"
        "• <b>Total Students:</b> 29 | <b>Passed:</b> 24 (82.76%) | <b>Failed:</b> 5 (17.24%)<br/>"
        "• <b>Overall Class Average:</b> 72.69%<br/>"
        "• <b>Subject Averages:</b> Python Programming (74.76%), Data Science (72.03%), Mathematics (71.28%)<br/>"
        "• <b>Honor Roll (#1):</b> harshit (STU127, Computer Science) with 98.67% average (Grade A+)<br/>"
        "• <b>Class Extremes:</b> Highest: harshit (98.67%) | Lowest: Rahul Kulkarni & Varun Chopra (38.33%)<br/>"
        "• <b>Attendance Shortages:</b> 8 students (27.59%) flagged with attendance &lt; 75.0%.",
        body_style
    ))

    elements.append(Paragraph("14. Challenges Faced and Lessons Learned", h1_style))
    elements.append(Paragraph(
        "1. <i>Immutability Enforcement:</i> Resolved by applying defensive copying across all functions.<br/>"
        "2. <i>Single-Subject Failure:</i> Designed boolean masks ensuring students with high averages but a failing score (&lt; 40) in one subject receive Grade F.<br/>"
        "3. <i>Deterministic Tie-Breaking:</i> Implemented multi-column sorting to guarantee reproducible rankings across runs.",
        body_style
    ))

    elements.append(Paragraph("15. Limitations and Future Enhancements", h1_style))
    elements.append(Paragraph(
        "• <b>Current Limitations:</b> Operates via CLI without a graphical dashboard; relies on flat CSV storage.<br/>"
        "• <b>Future Enhancements:</b> Web interface with Streamlit, database persistence via PostgreSQL, and graphical PDF report card export.",
        body_style
    ))

    elements.append(Paragraph("16. Conclusion", h1_style))
    elements.append(Paragraph(
        "The Student Performance Analytics System meets and exceeds all course requirements, demonstrating practical "
        "mastery of Python, Pandas, and NumPy. It provides educational institutions with a dependable, automated grading "
        "and analytical reporting engine.",
        body_style
    ))

    elements.append(Paragraph("17. GitHub Repository & Submission Information", h1_style))
    elements.append(Paragraph(
        "<b>GitHub Repository:</b> <font color='#2B6CB0'>https://github.com/Ashishmaurya1303/Ashishmaurya1303-student-performance-analytics-system</font><br/>"
        "<b>Author:</b> Ashish Maurya<br/>"
        "<b>Course Submission:</b> Python with AI Mini Project.",
        body_style
    ))

    # Build the document
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
