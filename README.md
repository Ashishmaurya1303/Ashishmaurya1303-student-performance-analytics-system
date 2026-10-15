# Student Performance Analytics System

A Python, Pandas, and NumPy mini project developed for the **Python with AI** course.

---

## 1. Project Overview & Objective

The **Student Performance Analytics System** is a command-line academic analytics tool designed to load, validate, analyze, and report student performance data from a CSV dataset. 

### Objective
- Automate grade calculation, status determination, and attendance evaluation.
- Clean and validate student data defensively without corrupting raw files.
- Apply consistent, transparent academic grading rules and attendance shortage flags.
- Provide educators with instant terminal summaries, rankings, and statistical distributions.

---

## 2. Features & Functional Requirements

- **CSV Ingestion**: Loads student records with format, existence, and schema validation.
- **Defensive Cleaning & Imputation**: Strips whitespace, rejects empty names or duplicate student IDs, validates scores in $[0, 100]$, and applies transparent median imputation for missing values.
- **Core Academic Calculations**:
  - Total marks across Mathematics, Python Programming, and Data Science.
  - Overall average marks (percentage).
  - Passing status determination (requires $\ge 40$ in every subject and $\ge 40\%$ overall).
  - 7-tier letter grading (A+, A, B, C, D, E, F).
  - Attendance evaluation (normal $\ge 75\%$, shortage $< 75\%$).
- **Cohort Analytics & Insights**:
  - Honor Roll (Top 3 students) with deterministic tie-breaking.
  - Highest and lowest performing students (including ties).
  - Subject-wise and overall class averages.
  - Pass/Fail rates and attendance shortage counts.
- **Clean Terminal Reporting**: Formatted, aligned ASCII tables and sectioned executive summaries.
- **Automated Verification**: Complete unit and integration test suite covering 27 test scenarios.

---

## 3. Technologies Used

- **Python 3.12+**: Core language, type hints, PEP 8 style.
- **Pandas**: Tabular data manipulation, CSV I/O, schema verification.
- **NumPy**: Vectorized mathematical calculations (`np.select`, `np.where`, array operations).
- **ReportLab & Pillow** *(Optional tools)*: For generating the official project PDF documentation and screenshots.

---

## 4. Project Directory Structure

```text
student_analytics_system/
├── data/
│   └── students.csv                # Student dataset with 26 records
├── docs/
│   └── screenshots/                # Terminal output screenshots
│       ├── screenshot_roster.png
│       ├── screenshot_insights.png
│       └── screenshot_tests.png
├── scripts/
│   ├── build_pdf.py                # PDF compilation script
│   └── generate_screenshots.py     # Terminal capture script
├── src/
│   ├── __init__.py                 # Package initializer
│   ├── data_loader.py              # Ingestion, validation, and cleaning
│   ├── analytics.py                # Totals, averages, grades, summaries
│   └── display.py                  # Formatted terminal display functions
├── tests/
│   ├── test_data_loader.py         # 10 unit tests for loader & cleaning
│   ├── test_analytics.py           # 11 unit tests for analytics & grading
│   └── test_end_to_end.py          # 6 end-to-end integration tests
├── main.py                         # Application CLI entry point
├── requirements.txt                # Project dependencies
├── README.md                       # Main documentation
├── Project_Documentation.md        # Detailed editable documentation
└── Project_Documentation.pdf       # Compiled publication-ready PDF report
```

---

## 5. Dataset Description & Columns

The dataset is located at [`data/students.csv`](file:///e:/Python%20with%20ai/student_analytics_system/data/students.csv) and contains 26 realistic records:

| Column Name | Type | Valid Range | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Unique string | Unique student ID (e.g., `STU101`) |
| `student_name` | String | Alphabetic text | Full name of the student |
| `department` | String | CS, AI, IT, DS | Academic department |
| `math_marks` | Float | `0.0` – `100.0` | Marks in Mathematics |
| `python_marks` | Float | `0.0` – `100.0` | Marks in Python Programming |
| `data_science_marks` | Float | `0.0` – `100.0` | Marks in Data Science |
| `attendance_pct` | Float | `0.0` – `100.0` | Attendance percentage |

---

## 6. Grading, Passing & Attendance Rules

### Passing Criteria
- A student **must score $\ge 40$ in EACH individual subject**.
- A student's **overall average must be $\ge 40\%$**.
- If any subject is $< 40$ or average is $< 40\%$, the student receives **Fail** and grade **F**.

### Grading Scale (For Passing Students)
| Average Range | Grade | Description |
| :---: | :---: | :--- |
| **$\ge 90.0\%$** | **A+** | Outstanding |
| **$80.0\% - 89.9\%$** | **A** | Excellent |
| **$70.0\% - 79.9\%$** | **B** | Very Good |
| **$60.0\% - 69.9\%$** | **C** | Good |
| **$50.0\% - 59.9\%$** | **D** | Satisfactory |
| **$40.0\% - 49.9\%$** | **E** | Pass |
| **$< 40.0\%$** (or failed any subject) | **F** | Fail |

### Attendance Criteria
- $\ge 75.0\%$: **Normal**
- $< 75.0\%$: **Shortage** (Flagged in advisory report)

---

## 7. Prerequisites & Installation (Windows)

### Prerequisites
- Python 3.12 or newer installed on Windows.
- Windows PowerShell.

### Step 1: Open Terminal in Project Root
```powershell
cd "E:\Python with ai\student_analytics_system"
```

### Step 2: Create a Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If script execution is disabled, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 8. Running the Application

To run the complete system and view the terminal report:

```powershell
python main.py
```

*(Note: The application dynamically resolves its dataset path relative to `main.py`, so you can also run it from any parent folder, e.g., `python student_analytics_system/main.py`).*

---

## 9. Running the Test Suites

All tests are automated and execute from the project root:

```powershell
# Run the complete end-to-end integration suite (runs all 27 tests)
python tests/test_end_to_end.py

# Run individual unit test modules
python tests/test_data_loader.py
python tests/test_analytics.py
```

---

## 10. Actual Program Execution Output

Below is an authentic sample of the terminal report output when running `python main.py`:

```text
==========================================================================================
           STUDENT PERFORMANCE ANALYTICS SYSTEM           
          Powered by Python, Pandas, and NumPy             
==========================================================================================

------------------------------------------------------------------------------------------
 1. COMPLETE STUDENT PERFORMANCE ROSTER
------------------------------------------------------------------------------------------
ID       Name               Department                Math   Pyth     DS   Total   Avg %  Grd  Status  Att % Att Stat
---------------------------------------------------------------------------------------------------------------------
STU101   Aarav Sharma       Computer Science          92.0   88.0   95.0   275.0   91.67  A+    Pass    94.5  Normal 
STU102   Diya Patel         Artificial Intelligence   78.0   85.0   82.0   245.0   81.67   A    Pass    88.0  Normal 
...
STU107   Vikram Singh       Information Technology    34.0   62.0   55.0   151.0   50.33   F    Fail    79.0  Normal 
...
---------------------------------------------------------------------------------------------------------------------
 Total records displayed: 26

------------------------------------------------------------------------------------------
 2. TOP PERFORMING STUDENTS (HONOR ROLL)
------------------------------------------------------------------------------------------
Rank   ID       Name                 Department                 Total  Average %  Grade 
----------------------------------------------------------------------------------------
#1     STU104   Ananya Iyer          Data Science               283.0     94.33%   A+   
#2     STU118   Kavya Menon          Artificial Intelligence    282.0     94.00%   A+   
#3     STU101   Aarav Sharma         Computer Science           275.0     91.67%   A+   
----------------------------------------------------------------------------------------

------------------------------------------------------------------------------------------
 3. HIGHEST AND LOWEST PERFORMERS (CLASS EXTREMES)
------------------------------------------------------------------------------------------
 Highest Performer(s):
   * Ananya Iyer (STU104, Data Science): Average = 94.33%, Total = 283.0, Grade = A+

 Lowest Performer(s):
   * Rahul Kulkarni (STU111, Information Technology): Average = 38.33%, Total = 115.0, Grade = F
   * Varun Chopra (STU117, Computer Science): Average = 38.33%, Total = 115.0, Grade = F
------------------------------------------------------------------------------------------

------------------------------------------------------------------------------------------
 4. SUBJECT-WISE CLASS AVERAGES
------------------------------------------------------------------------------------------
 Subject Name                  Class Average
---------------------------------------------
 Mathematics                          68.81%
 Python Programming                   72.73%
 Data Science                         71.77%
---------------------------------------------

------------------------------------------------------------------------------------------
 5. OVERALL CLASS AVERAGE
------------------------------------------------------------------------------------------
  Aggregated Cohort Average Score : 71.10%

------------------------------------------------------------------------------------------
 6. ACADEMIC OUTCOMES & PASS/FAIL DISTRIBUTION
------------------------------------------------------------------------------------------
  Total Enrolled Students : 26
  Students Passed         : 22    (84.62%)
  Students Failed         : 4     (15.38%)
------------------------------------------------------------------------------------------

------------------------------------------------------------------------------------------
 7. ATTENDANCE SHORTAGE ADVISORY (< 75.0% ATTENDANCE)
------------------------------------------------------------------------------------------
  Total Flagged Students: 7 (26.92% of cohort)
  ID       Name                 Department               Attendance
  -----------------------------------------------------------------
  STU105   Kabir Mehta          Computer Science              72.0%
  STU109   Aditya Nair          Computer Science              68.5%
  STU111   Rahul Kulkarni       Information Technology        60.0%
  STU114   Tanvi Sen            Artificial Intelligence       74.0%
  STU117   Varun Chopra         Computer Science              65.0%
  STU122   Simran Kaur          Artificial Intelligence       71.5%
  STU124   Neha Bhatt           Data Science                  70.0%
------------------------------------------------------------------------------------------

==========================================================================================
 8. EXECUTIVE SUMMARY & KEY TAKEAWAYS
==========================================================================================
  * Cohort Size           : 26 students
  * Pass Rate             : 84.62% (22 passed)
  * Fail Rate             : 15.38% (4 failed)
  * Overall Class Average : 71.10%
  * Attendance Shortages  : 7 students (26.92%)
==========================================================================================
[Success] Student Performance Analytics pipeline executed successfully.
```

## 11. Web Analytics Dashboard Enhancement

An interactive web analytics dashboard has been added on top of the existing Python system. It provides educators with a browser-based UI while reusing 100% of the underlying Python, Pandas, and NumPy processing logic.

### Architecture Overview

```text
Browser (HTML5, CSS3, Vanilla JS, Chart.js)
                      ↕ (HTTP REST API / Same-Origin Static)
Flask Web Server (`backend/app.py`)
                      ↕ (Direct Function Imports)
Existing Core Pipeline (`src.data_loader` & `src.analytics`)
                      ↕
Existing Dataset (`data/students.csv`)
```

- **Frontend (`frontend/`)**: Built strictly with semantic HTML5, custom responsive CSS3 (Inter & JetBrains Mono fonts, glassmorphism, mobile drawer, light/dark accents), and vanilla JavaScript. Interactive visual charts are rendered with Chart.js via CDN.
- **Backend API (`backend/app.py`)**: A lightweight Python Flask application serving both JSON endpoints (`/api/summary`, `/api/students`, `/api/analytics`, `/api/health`) and the frontend web assets from the same origin (`http://127.0.0.1:5000`).
- **Zero Calculation Duplication**: All calculations (totals, averages, 7-tier letter grades, pass/fail status, attendance shortage flags, honor roll rankings, extremes, and subject averages) are executed directly by `src/analytics.py` and `src/data_loader.py`.
- **API Test Suite (`backend/test_api.py`)**: 10 automated unit tests verifying API endpoints, filter queries, search queries, pagination, and error responses.

### Additional Technologies Added
- **Flask (>= 3.0.0)**: Lightweight WSGI web framework to expose REST endpoints and serve static frontend assets without requiring Node.js or external build tools.
- **Chart.js (4.4.2)**: Canvas-based charting library loaded via CDN for cohort visual analytics.

### Installation of Dependencies

To install all dependencies including Flask:

```powershell
pip install -r requirements.txt
```

### How to Run the Applications

#### 1. Running the Web Analytics Dashboard
Start the Flask backend server from the project root:

```powershell
python backend/app.py
```

Once running, open your web browser and navigate to:
**`http://127.0.0.1:5000`**

Features available on the web dashboard:
- **Executive Summary KPI Cards**: Live metrics for total students, pass rate, fail rate, cohort average, attendance shortages, and top student.
- **Interactive Visualizations**: Subject-wise averages, pass vs. fail donut chart, department comparison, and 7-tier grade distribution.
- **Top 3 Honor Roll**: Deterministic podium ranking cards with tie-breaking rules.
- **Attendance Shortage Advisory**: Highlights students below the 75% threshold.
- **Master Student Records Table**: Live search by name or ID, department dropdown filter, academic status filter, clickable sortable column headers, and pagination (10, 25, or all records per page).

#### 2. Running the Original Terminal Application
The original terminal application remains completely intact and functional:

```powershell
python main.py
```

#### 3. Running All Automated Test Suites
Run the test suites from the project root:

```powershell
# Run the complete end-to-end integration suite (27 tests)
python tests/test_end_to_end.py

# Run unit tests individually
python tests/test_data_loader.py
python tests/test_analytics.py

# Run the new Flask API test suite (10 tests)
python backend/test_api.py
```

---

## 12. Author & Submission Information

- **Author**: `[Author Name Placeholder — Replace with your name for course submission]`
- **Course**: Python with AI
- **Repository URL**: `[GitHub Repository URL Placeholder — Replace after pushing to GitHub]`
