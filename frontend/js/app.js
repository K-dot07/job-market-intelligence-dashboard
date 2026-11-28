const API_BASE_URL = "http://127.0.0.1:8000";

// 1. Fetch jobs from FastAPI
async function getJobs() {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/`);

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const jobs = await response.json();

    if (!Array.isArray(jobs)) {
      throw new Error("Invalid API response: expected an array");
    }

    return jobs;
  } catch (error) {
    console.error("Failed to fetch jobs:", error);
    throw error;
  }
}

// 2. Calculate dashboard statistics
function updateStatistics(jobs) {
  const totalJobs = jobs.length;

  const totalCompanies = new Set(
    jobs.map((job) => job.company_name).filter(Boolean),
  ).size;

  const totalLocations = new Set(
    jobs.map((job) => job.location).filter(Boolean),
  ).size;

  const today = new Date();
  const lastWeek = new Date();

  lastWeek.setDate(today.getDate() - 7);

  const newJobs = jobs.filter((job) => {
    if (!job.posted_date) return false;

    const postedDate = new Date(`${job.posted_date}T00:00:00`);

    return postedDate >= lastWeek && postedDate <= today;
  }).length;

  document.getElementById("totalJobs").textContent = totalJobs;
  document.getElementById("totalCompanies").textContent = totalCompanies;
  document.getElementById("totalLocations").textContent = totalLocations;
  document.getElementById("newJobs").textContent = newJobs;
}

// 3. Safely display text received from API
function escapeHTML(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character],
  );
}

// 4. Display recent job listings
function displayRecentJobs(jobs) {
  const recentJobsContainer = document.getElementById("recentJobsList");

  const sortedJobs = [...jobs].sort((a, b) => {
    return new Date(b.posted_date || 0) - new Date(a.posted_date || 0);
  });

  const recentJobs = sortedJobs.slice(0, 5);

  if (recentJobs.length === 0) {
    recentJobsContainer.textContent = "No jobs available.";
    return;
  }

  recentJobsContainer.innerHTML = recentJobs
    .map(
      (job) => `

        <div class="job-item">

            <div>
                <h3>${escapeHTML(job.job_title)}</h3>

                <p>
                    ${escapeHTML(job.company_name)}
                    ·
                    ${escapeHTML(job.location || "Location not specified")}
                </p>
            </div>

            <span>
                ${escapeHTML(job.posted_date || "Date unavailable")}
            </span>

            <a href="pages/job-details.html?id=${encodeURIComponent(job.id)}">
                View Details
            </a>

        </div>

    `,
    )
    .join("");
}

// 5. Load dashboard data
async function loadDashboard() {
  try {
    const jobs = await getJobs();

    updateStatistics(jobs);

    displayRecentJobs(jobs);
  } catch (error) {
    console.error("Dashboard error:", error);

    document.getElementById("recentJobsList").textContent =
      "Unable to load job data. Please check the API connection.";
  }
}

// 6. Start dashboard
loadDashboard();
