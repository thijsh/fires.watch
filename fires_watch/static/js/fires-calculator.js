// F.I.R.E.S. Calculator
function firesCalculate() {
  // Only POST if form is valid
  if (document.querySelectorAll(".form-check-input:invalid").length == 0) {
    const form = new FormData(document.getElementById("fires-calculator-form")); // Parse user input
    const entries = Object.fromEntries(form.entries()); // Create object from user input
    const csrftoken = entries["csrfmiddlewaretoken"]; // Extract CSRF token from object
    delete entries["csrfmiddlewaretoken"]; // Remove CSRF token from object
    const json = JSON.stringify(entries); // Convert object to JSON

    // Submit form data to backend API
    fetch("/api/fires/calculate/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: json,
    })
      .then((response) => response.json())
      .then((data) => {
        const result = data["fires_calculate_result"];
        // Parse results if needed and add to page
        var years = Math.round(result["months"] / 12);
        document.getElementById("results-months").innerHTML = years;
        document.getElementById("results-age").innerHTML = result["age"];
        var formatCurrency = new Intl.NumberFormat(undefined, {
          style: "currency",
          currency: "EUR",
        });
        const portfolioValue = formatCurrency.format(result["portfolio"]);
        document.getElementById("results-portfolio-value").innerHTML =
          portfolioValue;

        // If not yet visible, make results card visible
        if (
          document.getElementById("results-pane").classList.contains("d-none")
        ) {
          document.getElementById("results-pane").classList.remove("d-none");
        }

        // Debug
        console.log(result);
      });
  }

  // Prevent page reload
  return false;
}
