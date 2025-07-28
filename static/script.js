document.getElementById('predictionForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get form values
    const day = document.getElementById('day').value;
    const season = document.getElementById('season').value;
    const temperature = document.getElementById('temperature').value;
    const households = document.getElementById('households').value;

    // Send data to backend
    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day, season, temperature, households })
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        if (data.error) {
            // Display error message
            resultDiv.innerHTML = `<span class="error">${data.error.join('<br>')}</span>`;
        } else {
            // Display prediction result
            resultDiv.innerHTML = `
                <strong>Predicted Electricity Usage:</strong> ${data.predicted_usage_kwh} kWh<br>
                <strong>Total Cost:</strong> ₹${data.total_cost} (at ₹5/kWh)<br>
                <strong>Appliance Usage Equivalents:</strong><br>
                - Run a fan for ${data.appliance_usage.fan_hours} hours<br>
                - Light a bulb for ${data.appliance_usage.bulb_hours} hours<br>
                - Run a fridge for ${data.appliance_usage.fridge_hours} hours
            `;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = `<span class="error">An unexpected error occurred. Please try again.</span>`;
    });
});