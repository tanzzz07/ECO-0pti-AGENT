document.addEventListener("DOMContentLoaded", () => {

  const token = localStorage.getItem("token");
  

  if (!token) {
      window.location.href = "login.html";
      return;
  }

  const role = localStorage.getItem("role");

document.addEventListener("DOMContentLoaded", () => {

    if(role === "admin"){

        const adminBtn =
            document.getElementById("admin-btn");

        if(adminBtn){
            adminBtn.style.display =
                "inline-block";
        }
    }

});

  document
    .getElementById("logout-btn")
    .addEventListener("click", () => {

      localStorage.removeItem("token");
      localStorage.removeItem("role");
      localStorage.removeItem("username");

      window.location.href = "login.html";
    });

  // KEEP ALL YOUR EXISTING CODE BELOW THIS

document.addEventListener("DOMContentLoaded", () => {

  document
    .getElementById("logout-btn")
    .addEventListener("click", () => {

      localStorage.removeItem("token");

      window.location.href = "login.html";
    });
  const form = document.getElementById("analysis-form");
  const resultsArea = document.getElementById("results-area");

  // Update slider values dynamically
  document
    .getElementById("light_usage_hours_per_day")
    .addEventListener("input", (e) => {
      document.getElementById("light-usage-value").textContent = e.target.value;
    });
  document
    .getElementById("ac_usage_hours_per_day")
    .addEventListener("input", (e) => {
      document.getElementById("ac-usage-value").textContent = e.target.value;
    });

  // Function to clean and format text
  function formatText(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Convert **text** to <strong>text</strong>
      .replace(/\n/g, "<br>") // Convert line breaks
      .replace(/(\d+\.\s)/g, '<div class="action-item">$1') // Format numbered lists
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

  // Function to create clean HTML output
  function createCleanOutput(result) {
    return `
            <div class="results-container fade-in">
                <div class="result-header slide-down">
                    <h2>🎯 Analysis Complete</h2>
                </div>

                <div class="result-section decision-section slide-up" style="animation-delay: 0.1s">
                    <h3>📋 Recommendation</h3>
                    <div class="content-box">
                        ${formatText(result.final_decision)}
                    </div>
                </div>

                <div class="result-section optimizer-section slide-up" style="animation-delay: 0.2s">
                    <h3>⚡ Key Insights</h3>
                    <div class="highlight-box">
                        ${result.optimizer_output}
                    </div>
                </div>

                <div class="result-section emissions-section slide-up" style="animation-delay: 0.3s">
                    <h3>📊 Emissions Overview</h3>
                    <div class="emissions-grid">
                        <div class="emission-item bounce-in" style="animation-delay: 0.4s">
                            <div class="emission-value">${
                              result.emissions_breakdown.electricity
                            }</div>
                            <div class="emission-label">Electricity</div>
                        </div>
                        <div class="emission-item bounce-in" style="animation-delay: 0.5s">
                            <div class="emission-value">${
                              result.emissions_breakdown.transport
                            }</div>
                            <div class="emission-label">Transport</div>
                        </div>
                        <div class="emission-item bounce-in" style="animation-delay: 0.6s">
                            <div class="emission-value">${
                              result.emissions_breakdown.fuel
                            }</div>
                            <div class="emission-label">Fuel</div>
                        </div>
                        <div class="emission-item total bounce-in" style="animation-delay: 0.7s">
                            <div class="emission-value">${
                              result.total_emissions_kg_per_month
                            }</div>
                            <div class="emission-label">Total (kg/month)</div>
                        </div>
                    </div>
                </div>

                <div class="result-section suggestions-section slide-up" style="animation-delay: 0.8s">
                    <h3>💡 Action Items</h3>
                    
                    <div class="suggestion-category">
                        <h4>🔌 Electricity</h4>
                        <ul class="suggestion-list">
                            ${result.electricity_suggestions
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
                        <h4>🚗 Transport</h4>
                        <ul class="suggestion-list">
                            ${result.transport_suggestions
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
                        <h4>⛽ Fuel</h4>
                        <ul class="suggestion-list">
                            ${result.fuel_suggestions
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
                    <h3>🌱 Green Infrastructure</h3>
                    <div class="green-box">
                        ${result.greeninfra_suggestion}
                    </div>
                </div>
            </div>
        `;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevent default form submission

    resultsArea.style.display = "block";
    resultsArea.innerHTML =
      '<div class="loading">🔄 Analyzing your data...</div>';

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
    "Authorization": `Bearer ${token}`
},
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        let errMessage = `HTTP error! Status: ${response.status}`;
        try {
          const errData = await response.json();
          if (errData.error) errMessage = errData.error;
        } catch(e) {}
        throw new Error(errMessage);
      }

      const result = await response.json();

      // Use the clean HTML output instead of plain text
      resultsArea.innerHTML = createCleanOutput(result);

      console.log("Analysis completed successfully:", result);
    } catch (error) {
      resultsArea.innerHTML = `
                <div class="error-message">
                    <h3>❌ Error</h3>
                    <p>An error occurred while analyzing your data: ${error.message}</p>
                    <p>Please try again or check your internet connection.</p>
                </div>
            `;
      console.error("Error:", error);
    }
  });
});
