
const API_BASE_URL = "http://127.0.0.1:8000";

let locationChart;
let experienceChart;
let companyChart;
let skillsChart;

// Fetch jobs from FastAPI
async function getJobs() {
  const response = await fetch(`${API_BASE_URL}/jobs/?limit=100`);

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return await response.json();
}

// Calculate total statistics
function updateStatistics(jobs) {
  document.getElementById("analyticsTotalJobs").textContent = jobs.length;

  const companies = new Set(
    jobs.map((job) => job.company_name).filter(Boolean),
  );

  document.getElementById("analyticsCompanies").textContent = companies.size;
}

// Count values in a field
function countByField(jobs, field) {
  const counts = {};

  jobs.forEach((job) => {
    const value = job[field];

    if (value) {
      counts[value] = (counts[value] || 0) + 1;
    }
  });

  return counts;
}

// Count skills separately
function countSkills(jobs) {
  const counts = {};

  jobs.forEach((job) => {
    if (!job.skills) return;

    job.skills.split(",").forEach((skill) => {
      const name = skill.trim();

      if (name) {
        counts[name] = (counts[name] || 0) + 1;
      }
    });
  });

  return counts;
}

// Create a chart
function createChart(canvasId, type, labels, values, label) {
  const canvas = document.getElementById(canvasId);

  return new Chart(canvas, {
    type,
    data: {
      labels,
      datasets: [
        {
          label,
          data: values,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

// Generate all analytics charts
function generateCharts(jobs) {
  const locations = countByField(jobs, "location");
  const experiences = countByField(jobs, "experience_level");
  const companies = countByField(jobs, "company_name");
  const skills = countSkills(jobs);

  // Jobs by Location
  locationChart = createChart(
    "locationChart",
    "bar",
    Object.keys(locations),
    Object.values(locations),
    "Number of Jobs",
  );

  // Experience Distribution
  experienceChart = createChart(
    "experienceChart",
    "pie",
    Object.keys(experiences),
    Object.values(experiences),
    "Experience Levels",
  );

  // Jobs by Company
  companyChart = createChart(
    "companyChart",
    "bar",
    Object.keys(companies),
    Object.values(companies),
    "Number of Jobs",
  );

  // Most Demanded Skills
  const topSkills = Object.entries(skills)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  skillsChart = createChart(
    "skillsChart",
    "bar",
    topSkills.map((item) => item[0]),
    topSkills.map((item) => item[1]),
    "Skill Frequency",
  );
}

// Load analytics
async function loadAnalytics() {
  try {
    const jobs = await getJobs();

    updateStatistics(jobs);
    generateCharts(jobs);
  } catch (error) {
    console.error("Analytics error:", error);
  }
}

loadAnalytics();
