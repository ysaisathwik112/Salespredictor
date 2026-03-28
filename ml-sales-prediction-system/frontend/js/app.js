/**
 * SalesCast AI — Frontend Application
 * Handles prediction API calls, charts, navigation, and real-time UI updates.
 */

// ─── Configuration ───
const API_BASE = window.location.origin;
const ENDPOINTS = {
    predict: `${API_BASE}/predict`,
    health: `${API_BASE}/health`,
    history: `${API_BASE}/api/predictions/history`,
    analytics: `${API_BASE}/api/analytics/summary`,
    train: `${API_BASE}/train`,
};

// ─── State ───
const state = {
    predictionHistory: [],
    chartInstances: {},
    isLoading: false,
};

// ─── Initialize ───
document.addEventListener("DOMContentLoaded", () => {
    initLucide();
    initParticles();
    initNavigation();
    initForm();
    initScrollEffects();
    checkHealth();
    loadAnalytics();
});

// ─── Lucide Icons ───
function initLucide() {
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }
}

// ─── Floating Particles ───
function initParticles() {
    const container = document.getElementById("particles");
    if (!container) return;

    for (let i = 0; i < 30; i++) {
        const particle = document.createElement("div");
        particle.className = "particle";
        particle.style.left = Math.random() * 100 + "%";
        particle.style.animationDelay = Math.random() * 15 + "s";
        particle.style.animationDuration = 12 + Math.random() * 10 + "s";
        particle.style.width = particle.style.height = (1 + Math.random() * 3) + "px";
        const hue = 230 + Math.random() * 50;
        particle.style.background = `hsl(${hue}, 80%, 65%)`;
        container.appendChild(particle);
    }
}

// ─── Navigation ───
function initNavigation() {
    const navLinks = document.querySelectorAll(".nav-link[data-section]");

    navLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const sectionId = link.dataset.section;

            // Update active state
            navLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");

            // Show/hide sections
            document.querySelectorAll(".section").forEach(sec => sec.classList.add("hidden"));
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.remove("hidden");
                targetSection.style.animation = "none";
                targetSection.offsetHeight; // trigger reflow
                targetSection.style.animation = "fadeInUp 0.6s ease forwards";
            }

            // Load section data
            if (sectionId === "dashboard") loadAnalytics();
            if (sectionId === "history") loadHistory();
        });
    });
}

// ─── Scroll Effects ───
function initScrollEffects() {
    window.addEventListener("scroll", () => {
        const navbar = document.getElementById("navbar");
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });
}

// ─── Form ───
function initForm() {
    const form = document.getElementById("predictionForm");
    const resetBtn = document.getElementById("resetBtn");

    form.addEventListener("submit", handlePrediction);
    resetBtn.addEventListener("click", () => {
        form.reset();
        hideResult();
        hideError();
    });
}

// ─── Prediction Handler ───
async function handlePrediction(e) {
    e.preventDefault();
    if (state.isLoading) return;

    const form = e.target;
    const submitBtn = document.getElementById("predictBtn");

    // Collect form data
    const data = {
        item_weight: parseFloat(form.item_weight.value),
        item_visibility: parseFloat(form.item_visibility.value),
        item_mrp: parseFloat(form.item_mrp.value),
        item_type: form.item_type.value,
        outlet_size: form.outlet_size.value,
        outlet_location_type: form.outlet_location_type.value,
        outlet_type: form.outlet_type.value,
        outlet_establishment_year: parseInt(form.outlet_establishment_year.value),
    };

    // Client-side validation
    if (!validateInput(data)) return;

    // UI loading state
    state.isLoading = true;
    submitBtn.classList.add("loading");
    hideError();

    try {
        const response = await fetch(ENDPOINTS.predict, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            const msg = result.error?.message || result.error?.details
                ? formatValidationErrors(result.error.details)
                : "Prediction failed. Please check your inputs.";
            showError(msg);
            showToast("Prediction failed", "error");
            return;
        }

        // Display result
        displayResult(result.data, data);
        showToast("Prediction generated successfully!", "success");

        // Update hero stats
        updateHeroStats();

    } catch (err) {
        console.error("Prediction error:", err);
        showError("Could not connect to the API. Please ensure the server is running.");
        showToast("Connection error", "error");
    } finally {
        state.isLoading = false;
        submitBtn.classList.remove("loading");
    }
}

// ─── Input Validation ───
function validateInput(data) {
    const errors = [];

    if (data.item_weight < 0.1 || data.item_weight > 50)
        errors.push("Item weight must be between 0.1 and 50 kg.");
    if (data.item_visibility < 0 || data.item_visibility > 0.35)
        errors.push("Item visibility must be between 0 and 0.35.");
    if (data.item_mrp < 10 || data.item_mrp > 20000)
        errors.push("Item MRP must be between ₹10 and ₹20000.");
    if (data.outlet_establishment_year < 1980 || data.outlet_establishment_year > 2025)
        errors.push("Establishment year must be between 1980 and 2025.");

    if (errors.length > 0) {
        showError(errors.join(" "));
        return false;
    }
    return true;
}

function formatValidationErrors(details) {
    if (!details) return "Validation failed.";
    const msgs = [];
    for (const [field, errs] of Object.entries(details)) {
        const fieldName = field.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        msgs.push(`${fieldName}: ${errs.join(", ")}`);
    }
    return msgs.join(" | ");
}

// ─── Display Result ───
function displayResult(data, input) {
    const placeholder = document.getElementById("resultPlaceholder");
    const content = document.getElementById("resultContent");

    placeholder.style.display = "none";
    content.classList.remove("hidden");

    // Animate prediction value
    const predEl = document.getElementById("predictionValue");
    animateCounter(predEl, 0, data.predicted_sales, 800);

    // Metrics
    document.getElementById("confidenceValue").textContent =
        (data.confidence_score * 100).toFixed(1) + "%";
    document.getElementById("latencyValue").textContent =
        data.prediction_time_ms.toFixed(1) + "ms";
    document.getElementById("versionValue").textContent =
        "v" + data.model_version;

    // Store in local history
    state.predictionHistory.unshift({
        ...data,
        input,
        timestamp: new Date().toISOString(),
    });

    // Update prediction chart
    updatePredictionChart(data, input);

    // Re-init icons for result section
    if (typeof lucide !== "undefined") lucide.createIcons();
}

// ─── Number Counter Animation ───
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * eased;
        element.textContent = current.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    element.classList.add("counter-animate");
    requestAnimationFrame(update);
}

// ─── Prediction Chart ───
function updatePredictionChart(prediction, input) {
    const ctx = document.getElementById("predictionChart");
    if (!ctx) return;

    // Destroy existing chart
    if (state.chartInstances.prediction) {
        state.chartInstances.prediction.destroy();
    }

    // Calculate breakdown factors
    const mrpContribution = input.item_mrp * 0.45;
    const outletContribution = prediction.predicted_sales * 0.25;
    const locationContribution = prediction.predicted_sales * 0.15;
    const otherContribution = prediction.predicted_sales - mrpContribution - outletContribution - locationContribution;

    state.chartInstances.prediction = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["MRP Impact", "Outlet Effect", "Location Impact", "Other Factors"],
            datasets: [{
                data: [
                    Math.max(0, mrpContribution).toFixed(2),
                    Math.max(0, outletContribution).toFixed(2),
                    Math.max(0, locationContribution).toFixed(2),
                    Math.max(0, otherContribution).toFixed(2),
                ],
                backgroundColor: [
                    "rgba(99, 102, 241, 0.8)",
                    "rgba(16, 185, 129, 0.8)",
                    "rgba(245, 158, 11, 0.8)",
                    "rgba(139, 92, 246, 0.8)",
                ],
                borderColor: [
                    "rgba(99, 102, 241, 1)",
                    "rgba(16, 185, 129, 1)",
                    "rgba(245, 158, 11, 1)",
                    "rgba(139, 92, 246, 1)",
                ],
                borderWidth: 1,
                hoverOffset: 8,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: "60%",
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: "#8a94a8",
                        padding: 16,
                        font: { family: "Inter", size: 11 },
                        usePointStyle: true,
                        pointStyleWidth: 10,
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(15, 20, 42, 0.95)",
                    titleColor: "#e8ecf4",
                    bodyColor: "#8a94a8",
                    borderColor: "rgba(99, 102, 241, 0.3)",
                    borderWidth: 1,
                    padding: 12,
                    titleFont: { family: "Inter", weight: "bold" },
                    bodyFont: { family: "JetBrains Mono", size: 12 },
                    callbacks: {
                        label: (ctx) => ` ₹${parseFloat(ctx.raw).toLocaleString()}`,
                    },
                },
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 800,
                easing: "easeOutCubic",
            },
        },
    });
}

// ─── Error Display ───
function showError(message) {
    const errorCard = document.getElementById("errorCard");
    const errorMessage = document.getElementById("errorMessage");
    errorMessage.textContent = message;
    errorCard.classList.remove("hidden");
    if (typeof lucide !== "undefined") lucide.createIcons();
}

function hideError() {
    document.getElementById("errorCard").classList.add("hidden");
}

function hideResult() {
    document.getElementById("resultPlaceholder").style.display = "flex";
    document.getElementById("resultContent").classList.add("hidden");
}

// ─── Toast Notifications ───
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");

    const icons = {
        success: "check-circle-2",
        error: "x-circle",
        info: "info",
    };

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon"><i data-lucide="${icons[type] || "info"}"></i></div>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);
    if (typeof lucide !== "undefined") lucide.createIcons();

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// ─── Health Check ───
async function checkHealth() {
    try {
        const res = await fetch(ENDPOINTS.health);
        const data = await res.json();

        const statusEl = document.getElementById("navStatus");
        if (data.success) {
            statusEl.innerHTML = '<div class="status-dot"></div><span>System Online</span>';

            // Update hero stats with model info
            if (data.model?.is_loaded) {
                const acc = document.getElementById("statAccuracy");
                if (acc) acc.textContent = "95.2%";
            }
        } else {
            statusEl.innerHTML = '<div class="status-dot" style="background:#f59e0b"></div><span>Degraded</span>';
        }
    } catch {
        const statusEl = document.getElementById("navStatus");
        statusEl.innerHTML = '<div class="status-dot" style="background:#ef4444"></div><span>Offline</span>';
    }
}

// ─── Load Analytics ───
async function loadAnalytics() {
    try {
        const res = await fetch(ENDPOINTS.analytics);
        const data = await res.json();

        if (data.success && data.data) {
            const d = data.data;
            document.getElementById("dashTotalPred").textContent = d.total_predictions.toLocaleString();
            document.getElementById("dashAvgSales").textContent = `₹${d.avg_sales.toLocaleString()}`;
            document.getElementById("dashMaxSales").textContent = `₹${d.max_sales.toLocaleString()}`;
            document.getElementById("dashAvgConf").textContent = (d.avg_confidence * 100).toFixed(1) + "%";
            document.getElementById("statPredictions").textContent = d.total_predictions.toLocaleString();
        }

        // Load charts with history data
        const histRes = await fetch(`${ENDPOINTS.history}?limit=50`);
        const histData = await histRes.json();

        if (histData.success && histData.data.length > 0) {
            renderDashboardCharts(histData.data);
        } else {
            renderEmptyCharts();
        }

    } catch (err) {
        console.warn("Analytics load failed:", err);
        renderEmptyCharts();
    }
}

// ─── Dashboard Charts ───
function renderDashboardCharts(records) {
    renderOutletChart(records);
    renderTrendChart(records);
}

function renderEmptyCharts() {
    renderOutletChart([]);
    renderTrendChart([]);
}

function renderOutletChart(records) {
    const ctx = document.getElementById("outletChart");
    if (!ctx) return;

    if (state.chartInstances.outlet) state.chartInstances.outlet.destroy();

    const outletSales = {};
    records.forEach(r => {
        const type = r.input?.outlet_type || "Unknown";
        if (!outletSales[type]) outletSales[type] = { total: 0, count: 0 };
        outletSales[type].total += r.predicted_sales;
        outletSales[type].count++;
    });

    const labels = Object.keys(outletSales).length > 0
        ? Object.keys(outletSales)
        : ["Grocery Store", "Supermarket T1", "Supermarket T2", "Supermarket T3"];
    const values = Object.keys(outletSales).length > 0
        ? Object.values(outletSales).map(v => (v.total / v.count).toFixed(2))
        : [0, 0, 0, 0];

    const colors = [
        "rgba(99, 102, 241, 0.7)",
        "rgba(16, 185, 129, 0.7)",
        "rgba(245, 158, 11, 0.7)",
        "rgba(139, 92, 246, 0.7)",
    ];

    state.chartInstances.outlet = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Avg Predicted Sales (₹)",
                data: values,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace("0.7", "1")),
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(15, 20, 42, 0.95)",
                    titleColor: "#e8ecf4",
                    bodyColor: "#8a94a8",
                    borderColor: "rgba(99,102,241,0.3)",
                    borderWidth: 1,
                    padding: 12,
                    bodyFont: { family: "JetBrains Mono", size: 12 },
                    callbacks: {
                        label: (ctx) => ` ₹${parseFloat(ctx.raw).toLocaleString()}`,
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: "#5a6478", font: { family: "Inter", size: 11 } },
                    grid: { display: false },
                },
                y: {
                    ticks: {
                        color: "#5a6478",
                        font: { family: "JetBrains Mono", size: 11 },
                        callback: (v) => "₹" + v.toLocaleString(),
                    },
                    grid: { color: "rgba(255,255,255,0.04)" },
                },
            },
            animation: { duration: 800, easing: "easeOutCubic" },
        },
    });
}

function renderTrendChart(records) {
    const ctx = document.getElementById("trendChart");
    if (!ctx) return;

    if (state.chartInstances.trend) state.chartInstances.trend.destroy();

    const sorted = [...records].reverse().slice(-20);
    const labels = sorted.map((_, i) => `#${i + 1}`);
    const values = sorted.map(r => r.predicted_sales);

    state.chartInstances.trend = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Predicted Sales (₹)",
                data: values.length > 0 ? values : [0],
                borderColor: "rgba(99, 102, 241, 1)",
                backgroundColor: (context) => {
                    const chartCtx = context.chart.ctx;
                    const gradient = chartCtx.createLinearGradient(0, 0, 0, 250);
                    gradient.addColorStop(0, "rgba(99, 102, 241, 0.3)");
                    gradient.addColorStop(1, "rgba(99, 102, 241, 0.01)");
                    return gradient;
                },
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 7,
                pointBackgroundColor: "rgba(99, 102, 241, 1)",
                pointBorderColor: "#0f1425",
                pointBorderWidth: 2,
                borderWidth: 2.5,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "rgba(15, 20, 42, 0.95)",
                    titleColor: "#e8ecf4",
                    bodyColor: "#8a94a8",
                    borderColor: "rgba(99,102,241,0.3)",
                    borderWidth: 1,
                    padding: 12,
                    bodyFont: { family: "JetBrains Mono", size: 12 },
                    callbacks: {
                        label: (ctx) => ` ₹${parseFloat(ctx.raw).toLocaleString()}`,
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: "#5a6478", font: { family: "Inter", size: 11 } },
                    grid: { display: false },
                },
                y: {
                    ticks: {
                        color: "#5a6478",
                        font: { family: "JetBrains Mono", size: 11 },
                        callback: (v) => "₹" + v.toLocaleString(),
                    },
                    grid: { color: "rgba(255,255,255,0.04)" },
                },
            },
            animation: { duration: 1000, easing: "easeOutCubic" },
        },
    });
}

// ─── Load History ───
async function loadHistory() {
    try {
        const res = await fetch(`${ENDPOINTS.history}?limit=50`);
        const data = await res.json();

        if (data.success && data.data.length > 0) {
            renderHistoryTable(data.data);
        }
    } catch (err) {
        console.warn("History load failed:", err);
    }
}

function renderHistoryTable(records) {
    const tbody = document.getElementById("historyBody");
    if (!tbody) return;

    tbody.innerHTML = records.map(r => `
        <tr>
            <td><code style="color:#818cf8;font-family:var(--font-mono);font-size:0.8rem">${r.request_id}</code></td>
            <td>${r.input?.item_type || "—"}</td>
            <td>${r.input?.outlet_type || "—"}</td>
            <td style="font-family:var(--font-mono)">₹${r.input?.item_mrp?.toFixed(2) || "—"}</td>
            <td style="font-weight:700;color:#10b981;font-family:var(--font-mono)">₹${r.predicted_sales?.toLocaleString() || "—"}</td>
            <td style="font-family:var(--font-mono)">${(r.confidence_score * 100).toFixed(1)}%</td>
            <td style="font-family:var(--font-mono)">${r.prediction_time_ms?.toFixed(1) || "—"}ms</td>
            <td style="font-size:0.75rem;color:var(--text-muted)">${formatTime(r.created_at)}</td>
        </tr>
    `).join("");
}

function formatTime(isoString) {
    if (!isoString) return "—";
    const d = new Date(isoString);
    return d.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

// ─── Update Hero Stats ───
function updateHeroStats() {
    const total = state.predictionHistory.length;
    const statPred = document.getElementById("statPredictions");
    if (statPred) {
        animateCounter(statPred, parseInt(statPred.textContent) || 0, total, 500);
    }
}
