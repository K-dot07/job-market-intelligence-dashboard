const API_BASE_URL = "http://127.0.0.1:8000";

const jobDetails = document.getElementById("jobDetails");

// Safely display API data
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

// Get job ID from the URL
async function loadJobDetails() {
  const params = new URLSearchParams(window.location.search);
  const jobId = params.get("id");

  if (!jobId || !/^\d+$/.test(jobId) || Number(jobId) < 1) {
    jobDetails.textContent = "Invalid job ID.";
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/jobs/${encodeURIComponent(jobId)}`,
    );

    if (response.status === 404) {
      jobDetails.textContent = "Job not found.";
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const job = await response.json();

    displayJobDetails(job);
  } catch (error) {
    console.error("Job details error:", error);

    jobDetails.textContent =
      "Unable to load job details. Please check the API connection.";
  }
}

// Display selected job
function displayJobDetails(job) {
  const applyButton = job.apply_url
    ? `
            <a
                href="${escapeHTML(job.apply_url)}"
                target="_blank"
                rel="noopener noreferrer"
                class="apply-button"
            >
                Apply Now
            </a>
        `
    : "";

  jobDetails.innerHTML = `

        <div class="job-details-card">

            <div class="job-details-header">

                <h2>${escapeHTML(job.job_title)}</h2>

                <p>
                    ${escapeHTML(job.company_name)}
                    ·
                    ${escapeHTML(job.location || "Location not specified")}
                </p>

            </div>

            <div class="job-details-grid">

                <div class="detail-item">
                    <h4>Job ID</h4>
                    <p>${escapeHTML(job.id)}</p>
                </div>

                <div class="detail-item">
                    <h4>Experience Level</h4>
                    <p>${escapeHTML(job.experience_level || "Not specified")}</p>
                </div>

                <div class="detail-item">
                    <h4>Salary</h4>
                    <p>${escapeHTML(job.salary || "Not disclosed")}</p>
                </div>

                <div class="detail-item">
                    <h4>Posted Date</h4>
                    <p>${escapeHTML(job.posted_date || "Not available")}</p>
                </div>

                <div class="detail-item">
                    <h4>Source</h4>
                    <p>${escapeHTML(job.source_name || "Not specified")}</p>
                </div>

                <div class="detail-item">
                    <h4>Skills</h4>
                    <p>${escapeHTML(job.skills || "Not specified")}</p>
                </div>

            </div>

            <div class="job-description">

                <h3>Job Information</h3>

                <p>
                    Company: ${escapeHTML(job.company_name)}
                </p>

                <p>
                    Location: ${escapeHTML(job.location || "Not specified")}
                </p>

            </div>

            ${applyButton}

        </div>

    `;
}

// Start
loadJobDetails();
