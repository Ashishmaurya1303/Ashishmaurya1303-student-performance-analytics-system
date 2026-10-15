/**
 * Student Performance Analytics Dashboard - Frontend Orchestrator
 *
 * Consumes REST API endpoints from the Python Flask backend.
 * All calculations, grading, and stats are computed purely by Pandas/NumPy in Python.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    currentPage: 1,
    pageSize: 10,
    searchQuery: "",
    selectedDept: "all",
    selectedStatus: "all",
    sortBy: "student_id",
    sortOrder: "asc",
    departments: [],
    deleteTargetId: "",
    deleteTargetName: "",
    charts: {
      subjectAverages: null,
      outcomes: null,
      departments: null,
      grades: null,
    },
  };

  // DOM Elements
  const statusChip = document.getElementById("data-status-chip");
  const statusText = document.getElementById("status-text");
  const refreshBtn = document.getElementById("refresh-btn");
  const globalAlert = document.getElementById("global-alert-container");

  // KPI elements
  const kpiTotal = document.getElementById("kpi-total");
  const kpiPassed = document.getElementById("kpi-passed");
  const kpiPassedRate = document.getElementById("kpi-passed-rate");
  const kpiFailed = document.getElementById("kpi-failed");
  const kpiFailedRate = document.getElementById("kpi-failed-rate");
  const kpiAvg = document.getElementById("kpi-avg");
  const kpiShortages = document.getElementById("kpi-shortages");
  const kpiShortagesRate = document.getElementById("kpi-shortages-rate");
  const kpiTopName = document.getElementById("kpi-top-name");
  const kpiTopDetail = document.getElementById("kpi-top-detail");

  // Panels
  const honorRollContainer = document.getElementById("honor-roll-container");
  const highestPerformersContent = document.getElementById("highest-performers-content");
  const lowestPerformersContent = document.getElementById("lowest-performers-content");
  const shortageTableBody = document.getElementById("shortage-table-body");

  // Table & Controls
  const studentTableBody = document.getElementById("student-table-body");
  const searchInput = document.getElementById("student-search-input");
  const clearSearchBtn = document.getElementById("clear-search");
  const deptFilter = document.getElementById("dept-filter");
  const statusFilter = document.getElementById("status-filter");
  const pageSizeSelect = document.getElementById("page-size-select");
  const tableStatsInfo = document.getElementById("table-stats-info");
  const paginationContainer = document.getElementById("pagination-container");

  // Mobile sidebar
  const mobileToggle = document.getElementById("mobile-toggle");
  const sidebar = document.getElementById("sidebar");

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }

  // --------------------------------------------------------------------------
  // Utility Functions
  // --------------------------------------------------------------------------
  function setSystemStatus(isHealthy, message) {
    if (isHealthy) {
      statusChip.className = "status-chip";
      statusText.textContent = message || "Python Analytics Online";
    } else {
      statusChip.className = "status-chip error";
      statusText.textContent = message || "Backend Offline";
    }
  }

  function showAlert(message, type = "error") {
    globalAlert.innerHTML = `
      <div class="alert-banner alert-${type}">
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;font-size:1.1rem;color:inherit;">&times;</button>
      </div>
    `;
    if (type === "success") {
      setTimeout(() => { globalAlert.innerHTML = ""; }, 4000);
    }
  }

  function clearAlert() {
    globalAlert.innerHTML = "";
  }

  function getGradeBadgeClass(grade) {
    const cleanGrade = (grade || "").replace("+", "-plus");
    return `grade-badge grade-${cleanGrade}`;
  }

  // --------------------------------------------------------------------------
  // Fetch API Logic
  // --------------------------------------------------------------------------

  /** Fetch high-level summary KPIs computed by Python analytics.py */
  async function loadSummaryData() {
    try {
      const res = await fetch("/api/summary");
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || `HTTP ${res.status}`);
      }
      const json = await res.json();
      const d = json.data;

      // Populate KPIs
      kpiTotal.textContent = d.total_students;
      kpiPassed.textContent = d.passed_count;
      kpiPassedRate.textContent = `${d.passed_pct}%`;
      kpiFailed.textContent = d.failed_count;
      kpiFailedRate.textContent = `${d.failed_pct}%`;
      kpiAvg.textContent = `${d.class_average}%`;
      kpiShortages.textContent = d.attendance_shortages_count;
      kpiShortagesRate.textContent = `${d.attendance_shortages_pct}%`;

      if (d.highest_performers && d.highest_performers.length > 0) {
        const top1 = d.highest_performers[0];
        kpiTopName.textContent = top1.student_name;
        kpiTopDetail.textContent = `Avg: ${top1.average_marks}% | ${top1.department}`;
      }

      // Populate Extremes Spotlight
      renderExtremes(d.highest_performers, d.lowest_performers);
      setSystemStatus(true, "Python Analytics Online");
    } catch (err) {
      setSystemStatus(false, "Connection Failed");
      showAlert(`Failed to load executive summary: ${err.message}`);
    }
  }

  /** Render Highest and Lowest Performer spotlight */
  function renderExtremes(highestList, lowestList) {
    if (!highestList || highestList.length === 0) {
      highestPerformersContent.innerHTML = `<p class="text-muted">No data</p>`;
    } else {
      highestPerformersContent.innerHTML = highestList.map(s => `
        <div class="extreme-student-item">
          <div>
            <div class="extreme-student-name">${s.student_name} <span class="text-muted">(${s.student_id})</span></div>
            <div class="extreme-student-dept">${s.department}</div>
          </div>
          <div class="text-right">
            <span class="${getGradeBadgeClass(s.grade)}">${s.grade}</span>
            <div style="font-weight:800;color:var(--emerald-600);margin-top:2px;">${s.average_marks}%</div>
          </div>
        </div>
      `).join("");
    }

    if (!lowestList || lowestList.length === 0) {
      lowestPerformersContent.innerHTML = `<p class="text-muted">No data</p>`;
    } else {
      lowestPerformersContent.innerHTML = lowestList.map(s => `
        <div class="extreme-student-item">
          <div>
            <div class="extreme-student-name">${s.student_name} <span class="text-muted">(${s.student_id})</span></div>
            <div class="extreme-student-dept">${s.department}</div>
          </div>
          <div class="text-right">
            <span class="${getGradeBadgeClass(s.grade)}">${s.grade}</span>
            <div style="font-weight:800;color:var(--rose-600);margin-top:2px;">${s.average_marks}%</div>
          </div>
        </div>
      `).join("");
    }
  }

  /** Fetch visual analytics, distributions, and charts */
  async function loadAnalyticsData() {
    try {
      const res = await fetch("/api/analytics");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const d = json.data;

      // Render Honor Roll
      renderHonorRoll(d.top_performers);

      // Render Attendance Shortages Table
      renderShortages(d.attendance_shortages);

      // Render Chart.js Visualizations
      renderCharts(d);
    } catch (err) {
      console.error("Error loading analytics data:", err);
    }
  }

  /** Render Top 3 Honor Roll list */
  function renderHonorRoll(topPerformers) {
    if (!topPerformers || topPerformers.length === 0) {
      honorRollContainer.innerHTML = `<p class="text-muted">No records available.</p>`;
      return;
    }

    honorRollContainer.innerHTML = topPerformers.map((s, idx) => `
      <div class="honor-item">
        <div class="honor-left">
          <div class="rank-badge rank-${idx + 1}">#${idx + 1}</div>
          <div>
            <div class="honor-name">${s.student_name} <span class="text-muted">(${s.student_id})</span></div>
            <div class="honor-meta">${s.department}</div>
          </div>
        </div>
        <div class="honor-right">
          <div>
            <div class="honor-score">${s.average_marks}%</div>
            <div class="honor-total">Total: ${s.total_marks}/300</div>
          </div>
          <span class="${getGradeBadgeClass(s.grade)}">${s.grade}</span>
        </div>
      </div>
    `).join("");
  }

  /** Render Attendance Shortage Advisory records */
  function renderShortages(shortages) {
    if (!shortages || shortages.length === 0) {
      shortageTableBody.innerHTML = `
        <tr><td colspan="5" class="text-center text-muted" style="padding:16px;">
          All students meet the 75.0% attendance threshold.
        </td></tr>
      `;
      return;
    }

    shortageTableBody.innerHTML = shortages.map(s => `
      <tr>
        <td class="student-id-cell">${s.student_id}</td>
        <td class="student-name-cell">${s.student_name}</td>
        <td>${s.department}</td>
        <td class="text-right"><strong class="color-amber">${s.attendance_pct}%</strong></td>
        <td><span class="att-shortage">Shortage (&lt; 75%)</span></td>
      </tr>
    `).join("");
  }

  /** Render Interactive Chart.js Visualizations */
  function renderCharts(data) {
    // 1. Subject-wise class averages Bar Chart
    const subCanvas = document.getElementById("chart-subject-averages");
    if (subCanvas && data.subject_averages) {
      if (state.charts.subjectAverages) state.charts.subjectAverages.destroy();
      const labels = Object.keys(data.subject_averages);
      const values = Object.values(data.subject_averages);

      state.charts.subjectAverages = new Chart(subCanvas, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Class Average (%)",
            data: values,
            backgroundColor: ["#6366f1", "#10b981", "#0ea5e9"],
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { min: 0, max: 100, ticks: { callback: v => v + "%" } },
          },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => `Average: ${ctx.raw}%` } },
          },
        },
      });
    }

    // 2. Pass vs Fail Outcomes Doughnut Chart
    const outcomeCanvas = document.getElementById("chart-outcomes");
    if (outcomeCanvas && data.pass_fail) {
      if (state.charts.outcomes) state.charts.outcomes.destroy();

      state.charts.outcomes = new Chart(outcomeCanvas, {
        type: "doughnut",
        data: {
          labels: [`Pass (${data.pass_fail.passed})`, `Fail (${data.pass_fail.failed})`],
          datasets: [{
            data: [data.pass_fail.passed, data.pass_fail.failed],
            backgroundColor: ["#10b981", "#f43f5e"],
            borderWidth: 2,
            borderColor: "#ffffff",
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "bottom" },
          },
        },
      });
    }

    // 3. Department Comparison Grouped Bar Chart
    const deptCanvas = document.getElementById("chart-departments");
    if (deptCanvas && data.department_comparison) {
      if (state.charts.departments) state.charts.departments.destroy();

      const deptLabels = data.department_comparison.map(d => d.department);
      const deptAverages = data.department_comparison.map(d => d.overall_avg);
      const deptPassRates = data.department_comparison.map(d => d.pass_rate);

      state.charts.departments = new Chart(deptCanvas, {
        type: "bar",
        data: {
          labels: deptLabels,
          datasets: [
            {
              label: "Average Marks (%)",
              data: deptAverages,
              backgroundColor: "#818cf8",
              borderRadius: 4,
            },
            {
              label: "Pass Rate (%)",
              data: deptPassRates,
              backgroundColor: "#34d399",
              borderRadius: 4,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { min: 0, max: 100, ticks: { callback: v => v + "%" } },
          },
          plugins: {
            legend: { position: "bottom" },
          },
        },
      });
    }

    // 4. 7-Tier Grade Distribution Bar Chart
    const gradeCanvas = document.getElementById("chart-grades");
    if (gradeCanvas && data.grade_distribution) {
      if (state.charts.grades) state.charts.grades.destroy();

      const gradeLabels = data.grade_distribution.map(g => g.grade);
      const gradeCounts = data.grade_distribution.map(g => g.count);

      state.charts.grades = new Chart(gradeCanvas, {
        type: "bar",
        data: {
          labels: gradeLabels,
          datasets: [{
            label: "Students Count",
            data: gradeCounts,
            backgroundColor: [
              "#10b981", // A+
              "#34d399", // A
              "#60a5fa", // B
              "#facc15", // C
              "#fb923c", // D
              "#f472b6", // E
              "#f43f5e", // F
            ],
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1 } },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }
  }

  /** Fetch student roster records with filters, search, sorting, and pagination */
  async function loadStudentRecords() {
    studentTableBody.innerHTML = `<tr><td colspan="12" class="text-center py-4 text-muted">Loading records...</td></tr>`;

    try {
      const params = new URLSearchParams({
        page: state.currentPage,
        page_size: state.pageSize,
        dept: state.selectedDept,
        status: state.selectedStatus,
        search: state.searchQuery,
        sort_by: state.sortBy,
        order: state.sortOrder,
      });

      const res = await fetch(`/api/students?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const d = json.data;

      // Populate department dropdown once if not populated
      if (state.departments.length === 0 && d.departments) {
        state.departments = d.departments;
        deptFilter.innerHTML = `<option value="all">All Departments</option>` +
          d.departments.map(dept => `<option value="${dept}">${dept}</option>`).join("");
      }

      renderStudentTable(d);
    } catch (err) {
      studentTableBody.innerHTML = `<tr><td colspan="12" class="text-center py-4 color-rose">Failed to load student records: ${err.message}</td></tr>`;
      showAlert(`Error loading student records: ${err.message}`);
    }
  }

  /** Render Table rows and pagination */
  function renderStudentTable(data) {
    const students = data.students || [];

    if (students.length === 0) {
      studentTableBody.innerHTML = `
        <tr>
          <td colspan="13" class="text-center py-4" style="padding:40px 10px;">
            <div style="color:var(--text-muted);margin-bottom:8px;">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin:0 auto;display:block;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </div>
            <strong>No matching student records found</strong>
            <p class="text-muted" style="font-size:0.82rem;margin-top:4px;">Try adjusting your search query or removing active filters.</p>
          </td>
        </tr>
      `;
      tableStatsInfo.textContent = `Showing 0 of ${data.total_records} students`;
      paginationContainer.innerHTML = "";
      return;
    }

    studentTableBody.innerHTML = students.map(s => {
      const passPill = s.status === "Pass"
        ? `<span class="status-pill status-pass">&check; Pass</span>`
        : `<span class="status-pill status-fail">&times; Fail</span>`;

      const attStatus = s.attendance_status === "Shortage"
        ? `<span class="att-shortage">Shortage</span>`
        : `<span class="att-normal">Normal</span>`;

      return `
        <tr>
          <td class="student-id-cell">${s.student_id}</td>
          <td class="student-name-cell">${s.student_name}</td>
          <td>${s.department}</td>
          <td class="text-right">${s.math_marks.toFixed(1)}</td>
          <td class="text-right">${s.python_marks.toFixed(1)}</td>
          <td class="text-right">${s.data_science_marks.toFixed(1)}</td>
          <td class="text-right"><strong>${s.total_marks.toFixed(1)}</strong></td>
          <td class="text-right"><strong>${s.average_marks.toFixed(2)}%</strong></td>
          <td class="text-center"><span class="${getGradeBadgeClass(s.grade)}">${s.grade}</span></td>
          <td class="text-center">${passPill}</td>
          <td class="text-right">${s.attendance_pct.toFixed(1)}%</td>
          <td class="text-center">${attStatus}</td>
          <td class="text-center">
            <button class="delete-row-btn" data-id="${s.student_id}" data-name="${s.student_name}" title="Delete ${s.student_name}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            </button>
          </td>
        </tr>
      `;
    }).join("");

    // Attach delete button listeners for this page
    attachDeleteListeners();

    // Update Stats Label
    const startRecord = (data.page - 1) * data.page_size + 1;
    const endRecord = Math.min(startRecord + students.length - 1, data.filtered_records);
    tableStatsInfo.textContent = `Showing ${startRecord}–${endRecord} of ${data.filtered_records} filtered records (Total: ${data.total_records})`;

    // Render Pagination Controls
    renderPagination(data.page, data.total_pages);
  }

  /** Render Pagination buttons */
  function renderPagination(currentPage, totalPages) {
    if (totalPages <= 1) {
      paginationContainer.innerHTML = "";
      return;
    }

    let buttonsHtml = `
      <button class="page-btn" id="btn-prev-page" ${currentPage === 1 ? "disabled" : ""}>
        &laquo; Prev
      </button>
    `;

    for (let p = 1; p <= totalPages; p++) {
      buttonsHtml += `
        <button class="page-btn ${p === currentPage ? "active" : ""}" data-page="${p}">
          ${p}
        </button>
      `;
    }

    buttonsHtml += `
      <button class="page-btn" id="btn-next-page" ${currentPage === totalPages ? "disabled" : ""}>
        Next &raquo;
      </button>
    `;

    paginationContainer.innerHTML = buttonsHtml;

    // Attach listeners
    document.getElementById("btn-prev-page")?.addEventListener("click", () => {
      if (state.currentPage > 1) {
        state.currentPage--;
        loadStudentRecords();
      }
    });

    document.getElementById("btn-next-page")?.addEventListener("click", () => {
      if (state.currentPage < totalPages) {
        state.currentPage++;
        loadStudentRecords();
      }
    });

    paginationContainer.querySelectorAll(".page-btn[data-page]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const pageNum = parseInt(e.target.dataset.page, 10);
        if (pageNum !== state.currentPage) {
          state.currentPage = pageNum;
          loadStudentRecords();
        }
      });
    });
  }

  // --------------------------------------------------------------------------
  // Event Listeners for Filters, Search, Sorting
  // --------------------------------------------------------------------------

  // Search input debouncing
  let searchDebounceTimer = null;
  searchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    clearSearchBtn.style.display = val.length > 0 ? "block" : "none";

    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      state.searchQuery = val;
      state.currentPage = 1;
      loadStudentRecords();
    }, 250);
  });

  clearSearchBtn.addEventListener("click", () => {
    searchInput.value = "";
    clearSearchBtn.style.display = "none";
    state.searchQuery = "";
    state.currentPage = 1;
    loadStudentRecords();
  });

  // Department filter
  deptFilter.addEventListener("change", (e) => {
    state.selectedDept = e.target.value;
    state.currentPage = 1;
    loadStudentRecords();
  });

  // Status filter
  statusFilter.addEventListener("change", (e) => {
    state.selectedStatus = e.target.value;
    state.currentPage = 1;
    loadStudentRecords();
  });

  // Page size select
  pageSizeSelect.addEventListener("change", (e) => {
    state.pageSize = parseInt(e.target.value, 10);
    state.currentPage = 1;
    loadStudentRecords();
  });

  // Clickable Sortable Columns
  document.querySelectorAll("#master-student-table th.sortable").forEach(th => {
    th.addEventListener("click", () => {
      const sortCol = th.dataset.sort;
      if (state.sortBy === sortCol) {
        state.sortOrder = state.sortOrder === "asc" ? "desc" : "asc";
      } else {
        state.sortBy = sortCol;
        state.sortOrder = "asc";
      }

      // Update UI classes
      document.querySelectorAll("#master-student-table th.sortable").forEach(header => {
        header.classList.remove("sorted-asc", "sorted-desc");
        header.querySelector(".sort-icon").innerHTML = "&updownarrow;";
      });

      th.classList.add(state.sortOrder === "asc" ? "sorted-asc" : "sorted-desc");
      th.querySelector(".sort-icon").innerHTML = state.sortOrder === "asc" ? "&uarr;" : "&darr;";

      state.currentPage = 1;
      loadStudentRecords();
    });
  });

  // Refresh All Button
  refreshBtn.addEventListener("click", () => {
    clearAlert();
    loadSummaryData();
    loadAnalyticsData();
    loadStudentRecords();
  });

  // Smooth scroll active state highlighting in sidebar
  const navItems = document.querySelectorAll(".sidebar-nav .nav-item");
  const sections = document.querySelectorAll(".dashboard-section");

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute("id");
      }
    });

    navItems.forEach(item => {
      item.classList.remove("active");
      if (item.getAttribute("href") === `#${current}`) {
        item.classList.add("active");
      }
    });
  });

  // --------------------------------------------------------------------------
  // Add Student Modal Logic
  // --------------------------------------------------------------------------
  const addStudentBtn = document.getElementById("add-student-btn");
  const addStudentModal = document.getElementById("add-student-modal");
  const addStudentForm = document.getElementById("add-student-form");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalCancelBtn = document.getElementById("modal-cancel-btn");
  const modalSubmitBtn = document.getElementById("modal-submit-btn");
  const addFormError = document.getElementById("add-form-error");

  function openAddModal() {
    addStudentForm.reset();
    addFormError.style.display = "none";
    modalSubmitBtn.disabled = false;
    modalSubmitBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
      Add Student
    `;
    addStudentModal.classList.add("active");
  }

  function closeAddModal() {
    addStudentModal.classList.remove("active");
  }

  addStudentBtn.addEventListener("click", openAddModal);
  modalCloseBtn.addEventListener("click", closeAddModal);
  modalCancelBtn.addEventListener("click", closeAddModal);

  // Close modal on backdrop click
  addStudentModal.addEventListener("click", (e) => {
    if (e.target === addStudentModal) closeAddModal();
  });

  // Form submission handler
  addStudentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    addFormError.style.display = "none";

    const name = document.getElementById("input-student-name").value.trim();
    const dept = document.getElementById("input-department").value;
    const math = document.getElementById("input-math").value;
    const python = document.getElementById("input-python").value;
    const ds = document.getElementById("input-ds").value;
    const att = document.getElementById("input-attendance").value;

    // Client-side validation
    if (!name) {
      addFormError.textContent = "Student name is required.";
      addFormError.style.display = "block";
      return;
    }
    if (!dept) {
      addFormError.textContent = "Please select a department.";
      addFormError.style.display = "block";
      return;
    }

    const numericFields = { math_marks: math, python_marks: python, data_science_marks: ds, attendance_pct: att };
    for (const [key, val] of Object.entries(numericFields)) {
      if (val === "" || val === null || val === undefined) {
        addFormError.textContent = `${key.replace(/_/g, " ")} is required.`;
        addFormError.style.display = "block";
        return;
      }
      const n = parseFloat(val);
      if (isNaN(n) || n < 0 || n > 100) {
        addFormError.textContent = `${key.replace(/_/g, " ")} must be between 0 and 100.`;
        addFormError.style.display = "block";
        return;
      }
    }

    // Disable submit button
    modalSubmitBtn.disabled = true;
    modalSubmitBtn.innerHTML = `Adding...`;

    try {
      const res = await fetch("/api/students/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_name: name,
          department: dept,
          math_marks: parseFloat(math),
          python_marks: parseFloat(python),
          data_science_marks: parseFloat(ds),
          attendance_pct: parseFloat(att),
        }),
      });

      const json = await res.json();

      if (!res.ok || json.status !== "success") {
        throw new Error(json.message || `HTTP ${res.status}`);
      }

      closeAddModal();
      showAlert(`✓ ${json.message}`, "success");

      // Refresh all data
      state.departments = [];
      loadSummaryData();
      loadAnalyticsData();
      loadStudentRecords();

    } catch (err) {
      addFormError.textContent = err.message;
      addFormError.style.display = "block";
      modalSubmitBtn.disabled = false;
      modalSubmitBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
        Add Student
      `;
    }
  });

  // --------------------------------------------------------------------------
  // Delete Student Logic
  // --------------------------------------------------------------------------
  const deleteConfirmModal = document.getElementById("delete-confirm-modal");
  const deleteStudentName = document.getElementById("delete-student-name");
  const deleteStudentId = document.getElementById("delete-student-id");
  const deleteModalClose = document.getElementById("delete-modal-close");
  const deleteCancelBtn = document.getElementById("delete-cancel-btn");
  const deleteConfirmBtn = document.getElementById("delete-confirm-btn");

  function attachDeleteListeners() {
    document.querySelectorAll(".delete-row-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const target = e.currentTarget;
        state.deleteTargetId = target.dataset.id;
        state.deleteTargetName = target.dataset.name;
        deleteStudentName.textContent = state.deleteTargetName;
        deleteStudentId.textContent = `(${state.deleteTargetId})`;
        deleteConfirmBtn.disabled = false;
        deleteConfirmBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
          Delete Student
        `;
        deleteConfirmModal.classList.add("active");
      });
    });
  }

  function closeDeleteModal() {
    deleteConfirmModal.classList.remove("active");
    state.deleteTargetId = "";
    state.deleteTargetName = "";
  }

  deleteModalClose.addEventListener("click", closeDeleteModal);
  deleteCancelBtn.addEventListener("click", closeDeleteModal);
  deleteConfirmModal.addEventListener("click", (e) => {
    if (e.target === deleteConfirmModal) closeDeleteModal();
  });

  deleteConfirmBtn.addEventListener("click", async () => {
    if (!state.deleteTargetId) return;

    deleteConfirmBtn.disabled = true;
    deleteConfirmBtn.innerHTML = `Deleting...`;

    try {
      const res = await fetch(`/api/students/${encodeURIComponent(state.deleteTargetId)}`, {
        method: "DELETE",
      });

      const json = await res.json();

      if (!res.ok || json.status !== "success") {
        throw new Error(json.message || `HTTP ${res.status}`);
      }

      closeDeleteModal();
      showAlert(`✓ ${json.message}`, "success");

      // Refresh all data
      state.departments = [];
      loadSummaryData();
      loadAnalyticsData();
      loadStudentRecords();

    } catch (err) {
      closeDeleteModal();
      showAlert(`Failed to delete student: ${err.message}`);
    }
  });

  // Close modals on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (addStudentModal.classList.contains("active")) closeAddModal();
      if (deleteConfirmModal.classList.contains("active")) closeDeleteModal();
    }
  });

  // --------------------------------------------------------------------------
  // Initial Boot
  // --------------------------------------------------------------------------
  loadSummaryData();
  loadAnalyticsData();
  loadStudentRecords();
});
