/**
 * TubeTale Analytics - Chart Rendering
 * Uses Chart.js for data visualization
 */

// Growth Timeline Chart
function renderGrowthChart(data) {
    const ctx = document.getElementById('growthChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.year),
            datasets: [
                {
                    label: 'Subscribers',
                    data: data.map(d => d.subscribers),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4,
                    fill: true,
                },
                {
                    label: 'Videos',
                    data: data.map(d => d.videos),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#ffffff' }
                }
            },
            scales: {
                y: {
                    ticks: { color: '#9ca3af' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: {
                    ticks: { color: '#9ca3af' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

// Topic Distribution Chart
function renderTopicChart(data) {
    const ctx = document.getElementById('topicChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => d.value),
                backgroundColor: [
                    '#6366f1',
                    '#8b5cf6',
                    '#a78bfa',
                    '#c4b5fd',
                    '#ddd6fe',
                ],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#ffffff' }
                }
            }
        }
    });
}

// Battle Comparison Chart
function renderBattleChart(scores) {
    const ctx = document.getElementById('battleChart');
    if (!ctx) return;

    const categories = ['Quality', 'Consistency', 'Trust', 'Variety', 'Overall'];

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: categories,
            datasets: scores.map((score, index) => ({
                label: score.channelName,
                data: [
                    score.quality,
                    score.consistency,
                    score.trust,
                    score.variety,
                    score.overall
                ],
                borderColor: getChannelColor(index),
                backgroundColor: getChannelColor(index, 0.2),
                borderWidth: 2,
            }))
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#ffffff' }
                }
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        color: '#9ca3af',
                        backdropColor: 'transparent'
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { color: '#ffffff' }
                }
            }
        }
    });
}

// Helper: Get color for channel
function getChannelColor(index, alpha = 1) {
    const colors = [
        `rgba(99, 102, 241, ${alpha})`,    // primary
        `rgba(139, 92, 246, ${alpha})`,    // secondary
        `rgba(167, 139, 250, ${alpha})`,   // purple-400
        `rgba(196, 181, 253, ${alpha})`,   // purple-300
        `rgba(221, 214, 254, ${alpha})`,   // purple-200
    ];
    return colors[index % colors.length];
}
