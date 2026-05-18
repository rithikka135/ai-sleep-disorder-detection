/**
 * SleepSense AI - Main JavaScript
 */

// Auto-dismiss alerts after 5s
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach(el => {
    setTimeout(() => {
      el.style.transition = "opacity 0.5s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });

  // Animate KPI values counting up
  document.querySelectorAll(".kpi-value").forEach(el => {
    const raw = el.textContent.trim();
    const num = parseInt(raw.replace(/[^\d]/g, ""));
    if (!isNaN(num) && num > 0) {
      let start = 0;
      const step = Math.ceil(num / 40);
      const timer = setInterval(() => {
        start += step;
        if (start >= num) { el.textContent = raw; clearInterval(timer); return; }
        // Keep non-numeric suffix
        el.textContent = raw.replace(num.toString(), start.toString());
      }, 30);
    }
  });
});

// Form submit animation helper
function setLoading(btnId, text) {
  const btn = document.getElementById(btnId);
  if (btn) { btn.textContent = text; btn.disabled = true; }
}
