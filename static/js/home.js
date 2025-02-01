async function loadAnomalyChart() {
    try {
        const response = await fetch('/api/get_anomaly_stats');
        const result = await response.json();
        
        if (result.status === 'success') {
            const ctx = document.getElementById('anomalyChart').getContext('2d');
            
            const data = result.data;
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Anomaly Score',
                        data: data.anomaly_scores,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1,
                        pointBackgroundColor: data.is_anomaly.map(isAnomaly => 
                            isAnomaly ? 'red' : 'rgb(75, 192, 192)'
                        ),
                        pointRadius: data.is_anomaly.map(isAnomaly => 
                            isAnomaly ? 8 : 4
                        ),
                        pointHoverRadius: data.is_anomaly.map(isAnomaly => 
                            isAnomaly ? 10 : 6
                        )
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const index = context.dataIndex;
                                    const filename = data.filenames[index];
                                    const score = data.anomaly_scores[index].toFixed(3);
                                    const isAnomaly = data.is_anomaly[index];
                                    return [
                                        `File: ${filename}`,
                                        `Score: ${score}`,
                                        `Status: ${isAnomaly ? '⚠️ ANOMALY DETECTED' : 'Normal'}`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Anomaly Score'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Timestamp'
                            }
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading anomaly chart:', error);
    }
}

// Load chart when page loads
document.addEventListener('DOMContentLoaded', loadAnomalyChart);




function showAnomalyInsights() {
    const modal = document.getElementById('anomalyModal');
    const content = document.getElementById('anomalyInsightsContent');
    
    // Show loading state
    content.innerHTML = '<div class="text-center"><i class="ri-loader-4-line animate-spin text-3xl"></i></div>';
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Fetch anomaly insights from your backend
    fetch('/api/anomaly-insights')
        .then(response => response.json())
        .then(data => {
            content.innerHTML = generateAnomalyContent(data);
        })
        .catch(error => {
            content.innerHTML = '<div class="text-red-500">Error loading anomaly insights</div>';
            console.error('Error:', error);
        });
}

function closeAnomalyModal() {
    const modal = document.getElementById('anomalyModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function generateAnomalyContent(data) {
    // Example of how to generate content - modify based on your data structure
    return `
        <div class="grid grid-cols-2 gap-4">
            <div class="bg-zinc-800 p-4 rounded-lg">
                <h3 class="text-xl font-bold mb-2">Recent Anomalies</h3>
                <div class="space-y-2">
                    ${data.recentAnomalies.map(anomaly => `
                        <div class="border-l-4 border-red-500 pl-2">
                            <p class="font-semibold">${anomaly.type}</p>
                            <p class="text-sm text-gray-400">${anomaly.timestamp}</p>
                            <p>${anomaly.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="bg-zinc-800 p-4 rounded-lg">
                <h3 class="text-xl font-bold mb-2">Statistics</h3>
                <div class="space-y-2">
                    <p>Total Anomalies: ${data.stats.total}</p>
                    <p>Severity Distribution:</p>
                    <div class="flex gap-2">
                        <span class="text-red-500">High: ${data.stats.highSeverity}</span>
                        <span class="text-yellow-500">Medium: ${data.stats.mediumSeverity}</span>
                        <span class="text-green-500">Low: ${data.stats.lowSeverity}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('anomalyModal');
    if (e.target === modal) {
        closeAnomalyModal();
    }
});



function openAnomalyModal() {
    document.getElementById('anomalyModal').classList.remove('hidden');
    fetchAnomalyInsights();
}

function closeAnomalyModal() {
    document.getElementById('anomalyModal').classList.add('hidden');
}

function fetchAnomalyInsights() {
    fetch('/api/anomaly-insights')
        .then(response => response.json())
        .then(data => {
            const contentDiv = document.getElementById('anomalyInsightsContent');
            contentDiv.innerHTML = ''; // Clear previous content

            data.recentAnomalies.forEach(anomaly => {
                const anomalyDiv = document.createElement('div');
                anomalyDiv.classList.add('bg-zinc-800', 'p-4', 'rounded-lg', 'text-white');
                anomalyDiv.innerHTML = `
                    <h3 class="text-xl font-bold">${anomaly.type}</h3>
                    <p>${anomaly.description}</p>
                    <p class="text-sm text-zinc-400">${anomaly.timestamp}</p>
                `;
                contentDiv.appendChild(anomalyDiv);
            });
        })
        .catch(error => console.error('Error fetching anomaly insights:', error));
}



function showAnomalyDetails() {
    const modal = document.getElementById('anomalyDetailsModal');
    const detailsList = document.getElementById('anomalyDetailsList');
    
    // Show modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    // Show loading state
    detailsList.innerHTML = '<div class="text-center text-white">Loading anomaly details...</div>';
    
    // Fetch anomaly details
    fetch('/api/get-anomaly-details')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.anomalies.length === 0) {
                    detailsList.innerHTML = '<div class="text-center text-gray-400">No anomalies detected</div>';
                    return;
                }
                
                // Create HTML for each anomaly
                const anomaliesHTML = data.anomalies.map(anomaly => `
                    <div class="bg-zinc-800 p-4 rounded-lg border-l-4 ${getSeverityBorderColor(anomaly.severity)}">
                        <div class="flex justify-between items-start mb-2">
                            <h3 class="text-lg font-semibold text-white">${anomaly.filename}</h3>
                            <span class="px-2 py-1 rounded text-sm ${getSeverityBadgeColor(anomaly.severity)}">
                                ${anomaly.severity.toUpperCase()}
                            </span>
                        </div>
                        <p class="text-gray-300 mb-2">${anomaly.description}</p>
                        <div class="flex justify-between text-sm text-gray-400">
                            <span>Score: ${anomaly.anomaly_score}</span>
                            <span>${anomaly.timestamp}</span>
                        </div>
                    </div>
                `).join('');
                
                detailsList.innerHTML = anomaliesHTML;
            } else {
                detailsList.innerHTML = '<div class="text-center text-red-500">Error loading anomaly details</div>';
            }
        })
        .catch(error => {
            detailsList.innerHTML = '<div class="text-center text-red-500">Error loading anomaly details</div>';
            console.error('Error:', error);
        });
}

function closeAnomalyDetails() {
    const modal = document.getElementById('anomalyDetailsModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function getSeverityBorderColor(severity) {
    switch (severity.toLowerCase()) {
        case 'high':
            return 'border-red-600';
        case 'medium':
            return 'border-yellow-600';
        case 'low':
            return 'border-blue-600';
        default:
            return 'border-gray-600';
    }
}

function getSeverityBadgeColor(severity) {
    switch (severity.toLowerCase()) {
        case 'high':
            return 'bg-red-600/20 text-red-400';
        case 'medium':
            return 'bg-yellow-600/20 text-yellow-400';
        case 'low':
            return 'bg-blue-600/20 text-blue-400';
        default:
            return 'bg-gray-600/20 text-gray-400';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('anomalyDetailsModal');
    if (event.target === modal) {
        closeAnomalyDetails();
    }
});