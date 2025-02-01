
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/get_anomaly_stats')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const ctx = document.getElementById('anomalyChart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.data.labels,
                        datasets: [
                            {
                                label: 'Anomaly Score',
                                data: data.data.anomaly_scores,
                                borderColor: 'rgb(75, 192, 192)',
                                tension: 0.1,
                                pointBackgroundColor: data.data.is_anomaly.map(isAnomaly => 
                                    isAnomaly ? 'red' : 'rgb(75, 192, 192)'
                                ),
                                pointRadius: data.data.is_anomaly.map(isAnomaly => 
                                    isAnomaly ? 6 : 4
                                )
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const index = context.dataIndex;
                                        return [
                                            `File: ${data.data.filenames[index]}`,
                                            `Score: ${context.raw.toFixed(4)}`,
                                            `Anomaly: ${data.data.is_anomaly[index] ? 'Yes' : 'No'}`
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
                                },
                                ticks: {
                                    maxRotation: 45,
                                    minRotation: 45
                                }
                            }
                        }
                    }
                });
            }
        })
        .catch(error => console.error('Error fetching anomaly stats:', error));
});