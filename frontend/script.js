document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");
  const username = localStorage.getItem("username");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  // Set Profile Information in Header Navigation
  const usernameEl = document.getElementById("nav-username");
  const roleEl = document.getElementById("nav-role");
  const adminBtn = document.getElementById("admin-btn");
  const logoutBtn = document.getElementById("logout-btn");

  if (usernameEl && username) {
    usernameEl.textContent = username;
  }
  if (roleEl && role) {
    roleEl.textContent = role;
  }
  if (adminBtn && role === "admin") {
    adminBtn.style.display = "inline-flex";
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("username");
      window.location.href = "login.html";
    });
  }

  const form = document.getElementById("analysis-form");
  const resultsArea = document.getElementById("results-area");

  // Dynamic Range Slider Badges
  const lightRange = document.getElementById("light_usage_hours_per_day");
  const lightVal = document.getElementById("light-usage-value");
  if (lightRange && lightVal) {
    lightRange.addEventListener("input", (e) => {
      lightVal.textContent = e.target.value;
    });
  }

  const acRange = document.getElementById("ac_usage_hours_per_day");
  const acVal = document.getElementById("ac-usage-value");
  if (acRange && acVal) {
    acRange.addEventListener("input", (e) => {
      acVal.textContent = e.target.value;
    });
  }

  // Format Helper Functions
  function formatText(text) {
    if (!text) return "";
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>")
      .replace(/(\d+\.\s)/g, '<div class="action-item">$1')
      .replace(/\*\*Action:\*\*/g, '<div class="action-title">Action:</div>')
      .replace(/\*\*Impact:\*\*/g, '<div class="impact-title">Impact:</div>')
      .replace(
        /\*\*Summary of Carbon Footprint:\*\*/g,
        '<div class="summary-title">Summary of Carbon Footprint:</div>'
      )
      .replace(
        /\*\*Prioritized Sustainability Plan:\*\*/g,
        '<div class="plan-title">Prioritized Sustainability Plan:</div>'
      );
  }

  function createCleanOutput(result) {
    return `
      <div class="results-container fade-in">
        <div class="result-header slide-down">
          <h2>🎯 Carbon Emission Analysis Complete</h2>
        </div>

        <div class="result-section decision-section slide-up" style="animation-delay: 0.1s">
          <h3>📋 Prioritized Sustainability Plan</h3>
          <div class="content-box">
            ${formatText(result.final_decision)}
          </div>
        </div>

        <div class="result-section optimizer-section slide-up" style="animation-delay: 0.2s">
          <h3>⚡ Key Optimizer Insights</h3>
          <div class="highlight-box">
            ${result.optimizer_output || ""}
          </div>
        </div>

        <div class="result-section emissions-section slide-up" style="animation-delay: 0.3s">
          <h3>📊 Monthly Emissions Breakdown</h3>
          <div class="emissions-grid">
            <div class="emission-item bounce-in" style="animation-delay: 0.4s">
              <div class="emission-value">${result.emissions_breakdown?.electricity || 0}</div>
              <div class="emission-label">Electricity (kg CO₂)</div>
            </div>
            <div class="emission-item bounce-in" style="animation-delay: 0.5s">
              <div class="emission-value">${result.emissions_breakdown?.transport || 0}</div>
              <div class="emission-label">Transport (kg CO₂)</div>
            </div>
            <div class="emission-item bounce-in" style="animation-delay: 0.6s">
              <div class="emission-value">${result.emissions_breakdown?.fuel || 0}</div>
              <div class="emission-label">Fuel (kg CO₂)</div>
            </div>
            <div class="emission-item total bounce-in" style="animation-delay: 0.7s">
              <div class="emission-value">${result.total_emissions_kg_per_month || 0}</div>
              <div class="emission-label">Total Emissions (kg CO₂/mo)</div>
            </div>
          </div>
        </div>

        <div class="result-section suggestions-section slide-up" style="animation-delay: 0.8s">
          <h3>💡 Action Items & Mitigation Strategies</h3>
          
          <div class="suggestion-category">
            <h4>🔌 Electricity Efficiency</h4>
            <ul class="suggestion-list">
              ${(result.electricity_suggestions || [])
                .map(
                  (suggestion, index) =>
                    `<li class="slide-in-left" style="animation-delay: ${
                      0.9 + index * 0.1
                    }s">${suggestion}</li>`
                )
                .join("")}
            </ul>
          </div>

          <div class="suggestion-category">
            <h4>🚗 Fleet & Transport Optimization</h4>
            <ul class="suggestion-list">
              ${(result.transport_suggestions || [])
                .map(
                  (suggestion, index) =>
                    `<li class="slide-in-left" style="animation-delay: ${
                      1.1 + index * 0.1
                    }s">${suggestion}</li>`
                )
                .join("")}
            </ul>
          </div>

          <div class="suggestion-category">
            <h4>⛽ Fuel & Generator Recommendations</h4>
            <ul class="suggestion-list">
              ${(result.fuel_suggestions || [])
                .map(
                  (suggestion, index) =>
                    `<li class="slide-in-left" style="animation-delay: ${
                      1.3 + index * 0.1
                    }s">${suggestion}</li>`
                )
                .join("")}
            </ul>
          </div>
        </div>

        <div class="result-section green-infra-section slide-up" style="animation-delay: 1.5s">
          <h3>🌱 Green Infrastructure Guidance</h3>
          <div class="green-box">
            ${result.greeninfra_suggestion || "No green infrastructure suggestions."}
          </div>
        </div>
      </div>
    `;
  }

  if (form && resultsArea) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add("is-loading");
      }

      resultsArea.style.display = "block";
      resultsArea.innerHTML =
        '<div class="loading">🔄 Running AI Carbon Analysis & Optimization Engine...</div>';

      const formData = new FormData(form);
      const data = {};

      formData.forEach((value, key) => {
        if (value === "true") {
          data[key] = true;
        } else if (value === "false") {
          data[key] = false;
        } else {
          data[key] = isNaN(Number(value)) ? value : Number(value);
        }
      });

      try {
        const response = await fetch("/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          let errMessage = `HTTP error! Status: ${response.status}`;
          try {
            const errData = await response.json();
            if (errData.error) errMessage = errData.error;
          } catch (e) {}
          throw new Error(errMessage);
        }

        const result = await response.json();
        resultsArea.innerHTML = createCleanOutput(result);
        resultsArea.scrollIntoView({ behavior: "smooth", block: "start" });
      } catch (error) {
        resultsArea.innerHTML = `
          <div class="error-message" style="background: #fff0f0; border: 1px solid #f5c6c6; border-radius: 14px; padding: 20px; color: #9b3434;">
            <h3>❌ Analysis Error</h3>
            <p>An error occurred while analyzing your data: ${error.message}</p>
            <p style="margin-top: 8px; font-size: 0.88rem; color: #752929;">Please verify your input values and server connection.</p>
          </div>
        `;
        console.error("Analysis Error:", error);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.classList.remove("is-loading");
        }
      }
    });
  }
});
