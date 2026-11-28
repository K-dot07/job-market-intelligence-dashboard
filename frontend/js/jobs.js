
const API_BASE_URL = "http://127.0.0.1:8000";

const searchTitle = document.getElementById("searchTitle");
const searchLocation = document.getElementById("searchLocation");
const experienceFilter = document.getElementById("experienceFilter");
const companyFilter = document.getElementById("companyFilter");
const skillsFilter = document.getElementById("skillsFilter");

const searchButton = document.getElementById("searchButton");
const clearFilters = document.getElementById("clearFilters");
const sortBy = document.getElementById("sortBy");
const sortOrder = document.getElementById("sortOrder");

const jobResults = document.getElementById("jobResults");
const jobCount = document.getElementById("jobCount");

const previousPage = document.getElementById("previousPage");
const nextPage = document.getElementById("nextPage");
const pageInfo = document.getElementById("pageInfo");

const PAGE_SIZE = 10;
let currentOffset = 0;
let currentJobs = [];

// Escape text received from the API
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

// Build search parameters
function buildSearchParams() {
    const params = new URLSearchParams();

    if (searchTitle.value.trim()) {
        params.append("job_title", searchTitle.value.trim());
    }

    if (searchLocation.value.trim()) {
        params.append("location", searchLocation.value.trim());
    }

    if (experienceFilter.value) {
        params.append("experience_level", experienceFilter.value);
    }

    if (companyFilter.value.trim()) {
        params.append("company", companyFilter.value.trim());
    }

    if (skillsFilter.value.trim()) {
        params.append("skills", skillsFilter.value.trim());
    }

    params.append("limit", PAGE_SIZE);
    params.append("offset", currentOffset);
    params.append("sort_by", sortBy.value);
    params.append("sort_order", sortOrder.value);

    return params;
}

// Fetch jobs
async function searchJobs() {
    jobResults.textContent = "Loading jobs...";
    searchButton.disabled = true;

    try {
        const params = buildSearchParams();

        const response = await fetch(
            `${API_BASE_URL}/jobs/?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const jobs = await response.json();

        if (!Array.isArray(jobs)) {
            throw new Error("Invalid API response");
        }

        currentJobs = jobs;

        displayJobs(jobs);
        updatePagination(jobs);

    } catch (error) {
        console.error("Job search error:", error);

        jobResults.textContent =
            "Unable to load jobs. Please check the API connection.";

        jobCount.textContent = "Search failed";

    } finally {
        searchButton.disabled = false;
    }
}

// Display job cards
function displayJobs(jobs) {
    jobCount.textContent = `${jobs.length} jobs found on this page`;

    if (jobs.length === 0) {
        jobResults.textContent = "No matching jobs found.";
        return;
    }

    jobResults.innerHTML = jobs.map(job => `
        <article class="job-card">
            <div class="job-card-header">
                <div>
                    <h3>${escapeHTML(job.job_title)}</h3>
                    <p class="company-name">
                        ${escapeHTML(job.company_name)}
                    </p>
                </div>

                <span class="experience-badge">
                    ${escapeHTML(job.experience_level || "Not specified")}
                </span>
            </div>

            <div class="job-meta">
                <span>📍 ${escapeHTML(job.location || "Location not specified")}</span>
                <span>💰 ${escapeHTML(job.salary || "Not disclosed")}</span>
            </div>

            <p class="job-skills">
                <strong>Skills:</strong>
                ${escapeHTML(job.skills || "Not specified")}
            </p>

            <div class="job-card-footer">
                <span>
                    Posted: ${escapeHTML(job.posted_date || "Unknown")}
                </span>

                <a href="job-details.html?id=${encodeURIComponent(job.id)}">
                    View Details
                </a>
            </div>
        </article>
    `).join("");
}

// Update pagination controls
function updatePagination(jobs) {
    const currentPage = Math.floor(currentOffset / PAGE_SIZE) + 1;

    pageInfo.textContent = `Page ${currentPage}`;

    previousPage.disabled = currentOffset === 0;

    // A full page means another page may exist.
    // The next request confirms whether more records exist.
    nextPage.disabled = jobs.length < PAGE_SIZE;
}

// Clear all filters
function resetFilters() {
    searchTitle.value = "";
    searchLocation.value = "";
    experienceFilter.value = "";
    companyFilter.value = "";
    skillsFilter.value = "";

    sortBy.value = "id";
    sortOrder.value = "asc";

    currentOffset = 0;

    searchJobs();
}

// Search button
searchButton.addEventListener("click", () => {
    currentOffset = 0;
    searchJobs();
});

// Clear Filters button
clearFilters.addEventListener("click", resetFilters);

// Sorting controls
sortBy.addEventListener("change", () => {
    currentOffset = 0;
    searchJobs();
});

sortOrder.addEventListener("change", () => {
    currentOffset = 0;
    searchJobs();
});

// Experience filter
experienceFilter.addEventListener("change", () => {
    currentOffset = 0;
    searchJobs();
});

// Enter key support
[
    searchTitle,
    searchLocation,
    companyFilter,
    skillsFilter
].forEach(input => {
    input.addEventListener("keydown", event => {
        if (event.key === "Enter") {
            currentOffset = 0;
            searchJobs();
        }
    });
});

// Previous page
previousPage.addEventListener("click", () => {
    if (currentOffset >= PAGE_SIZE) {
        currentOffset -= PAGE_SIZE;
        searchJobs();
    }
});

// Next page
nextPage.addEventListener("click", () => {
    if (currentJobs.length === PAGE_SIZE) {
        currentOffset += PAGE_SIZE;
        searchJobs();
    }
});

// Load jobs when the page opens
searchJobs();
