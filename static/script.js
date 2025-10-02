// -------------------------------
// Module Navigation
// -------------------------------
const links = document.querySelectorAll(".nav-link");
const modules = document.querySelectorAll(".module");

links.forEach(link => {
    link.addEventListener("click", function() {
        const target = this.dataset.module;
        modules.forEach(m => m.classList.remove("active"));
        document.getElementById(target).classList.add("active");
    });
});

// -------------------------------
// Predict Flood
// -------------------------------
document.getElementById("predict-btn").addEventListener("click", async function() {
    const formData = {};
    const inputs = document.querySelectorAll("#predict-form input, #predict-form select");

    // Collect all input values
    inputs.forEach(input => {
        formData[input.name] = input.value;
    });

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        // Display prediction
        document.getElementById("prediction-result").innerHTML =
            result.error
                ? `<p style="color:red;">Error: ${result.error}</p>`
                : `<p><b>Predicted Flood Occurrence:</b> ${result.prediction}<br>
                   <b>Probability:</b> ${result.probability}</p>`;
    } catch (err) {
        document.getElementById("prediction-result").innerHTML =
            `<p style="color:red;">Request failed: ${err}</p>`;
    }
});
