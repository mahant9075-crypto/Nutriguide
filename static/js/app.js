document.addEventListener('DOMContentLoaded', () => {
    const medicalForm = document.getElementById('medicalForm');
    const feedbackForm = document.getElementById('feedbackForm');
    const resultsSection = document.getElementById('results');
    const predictionText = document.getElementById('predictionText');
    const eatList = document.getElementById('eatList');
    const avoidList = document.getElementById('avoidList');
    const reasonText = document.getElementById('reasonText');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    let currentMedicalData = null;
    let currentPrediction = null;

    medicalForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(medicalForm);
        const data = Object.fromEntries(formData.entries());

        // Convert types
        data.age = parseInt(data.age);
        data.height = parseFloat(data.height);
        data.weight = parseFloat(data.weight);
        if (data.sugar_level) data.sugar_level = parseFloat(data.sugar_level);
        else delete data.sugar_level;

        currentMedicalData = data;

        try {
            // 1. Get Prediction
            const predictRes = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const predictResult = await predictRes.json();
            currentPrediction = predictResult.prediction;

            predictionText.textContent = currentPrediction;

            // 2. Get Recommendations
            const recommendRes = await fetch(`/recommend?disease=${currentPrediction}`, {
                method: 'POST'
            });
            const recommendResult = await recommendRes.json();

            // Update UI
            eatList.innerHTML = recommendResult.eat.map(item => `<li>${item}</li>`).join('');
            avoidList.innerHTML = recommendResult.avoid.map(item => `<li>${item}</li>`).join('');
            reasonText.textContent = recommendResult.reason;

            // Show Results
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing your data.');
        }
    });

    downloadReportBtn.addEventListener('click', async () => {
        if (!currentMedicalData || !currentPrediction) return;

        try {
            const response = await fetch(`/report?prediction=${currentPrediction}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentMedicalData)
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "MedicalReport.pdf";
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert('Failed to generate report.');
            }
        } catch (error) {
            console.error('Error downloading report:', error);
        }
    });

    feedbackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(feedbackForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                alert('Thank you for your feedback!');
                feedbackForm.reset();
            } else {
                alert('Failed to submit feedback.');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    });

    // Search Functionality
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    let debounceTimer;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();

        if (query.length === 0) {
            searchSuggestions.classList.add('hidden');
            searchSuggestions.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.results && data.results.length > 0) {
                    searchSuggestions.innerHTML = data.results.map(disease => `
                        <div class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-100 text-gray-900" onclick="selectDisease('${disease}')">
                            <span class="block truncate font-normal">${disease}</span>
                        </div>
                    `).join('');
                    searchSuggestions.classList.remove('hidden');
                } else {
                    searchSuggestions.classList.add('hidden');
                }
            } catch (error) {
                console.error('Error searching:', error);
            }
        }, 300); // 300ms debounce
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            searchSuggestions.classList.add('hidden');
        }
    });

    // Make selectDisease global so it can be called from inline onclick
    window.selectDisease = async (disease) => {
        searchInput.value = disease;
        searchSuggestions.classList.add('hidden');

        try {
            // Update prediction text to show selected disease
            predictionText.textContent = disease;
            currentPrediction = disease; // Update global state for report generation

            // Fetch recommendations
            const recommendRes = await fetch(`/recommend?disease=${encodeURIComponent(disease)}`, {
                method: 'POST'
            });
            const recommendResult = await recommendRes.json();

            // Update UI
            eatList.innerHTML = recommendResult.eat.map(item => `<li>${item}</li>`).join('');
            avoidList.innerHTML = recommendResult.avoid.map(item => `<li>${item}</li>`).join('');
            reasonText.textContent = recommendResult.reason;

            // Show Results
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });

            // Clear medical data since we bypassed the form
            currentMedicalData = { name: "Guest", age: 0, height: 0, weight: 0, blood_group: "Unknown" };

        } catch (error) {
            console.error('Error fetching recommendations:', error);
            alert('Could not load recommendations for this disease.');
        }
    };
});
