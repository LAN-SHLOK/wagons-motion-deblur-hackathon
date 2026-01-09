export const initChart = (canvas, dataPoints) => {
    if (!canvas || !dataPoints) return null;
    
    const ctx = canvas.getContext('2d');
    
    const chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dataPoints.map((_, i) => `F${i + 1}`),
            datasets: [{
                label: 'PSNR (dB)',
                data: dataPoints,
                borderColor: '#22d3ee',
                backgroundColor: 'rgba(34, 211, 238, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 4,
                pointBackgroundColor: '#22d3ee',
                pointBorderColor: '#0f172a',
                pointBorderWidth: 2,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#22d3ee',
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#22d3ee',
                    bodyColor: '#94a3b8',
                    borderColor: '#22d3ee',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `PSNR: ${context.parsed.y.toFixed(1)} dB`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return value.toFixed(0) + ' dB';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 10
                        },
                        maxRotation: 0
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    
    return chartInstance;
};

export const updateChart = (chartInstance, newData) => {
    if (!chartInstance) return;
    
    chartInstance.data.labels = newData.map((_, i) => `F${i + 1}`);
    chartInstance.data.datasets[0].data = newData;
    chartInstance.update();
};