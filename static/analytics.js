// Parse chart data from JSON block
document.addEventListener('DOMContentLoaded', function() {
    const chartData = JSON.parse(document.getElementById('chart-data').textContent);

    // Type Chart (Doughnut)
    const typeCtx = document.getElementById('typeChart').getContext('2d');
    new Chart(typeCtx, {
        type: 'doughnut',
        data: {
            labels: chartData.typeLabels,
            datasets: [{
                data: chartData.typeCounts,
                backgroundColor: ['#38a169', '#3182ce', '#dd6b20', '#805ad5', '#e53e3e', '#38b2ac', '#d69e2e'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#4a5568' }
                }
            }
        }
    });

    // Status Chart (Pie)
    const statusCtx = document.getElementById('statusChart').getContext('2d');
    new Chart(statusCtx, {
        type: 'pie',
        data: {
            labels: chartData.statusLabels,
            datasets: [{
                data: chartData.statusCounts,
                backgroundColor: ['#dd6b20', '#38a169', '#3182ce', '#e53e3e'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#4a5568' }
                }
            }
        }
    });

    // Weekly Chart (Bar)
    const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
    new Chart(weeklyCtx, {
        type: 'bar',
        data: {
            labels: chartData.weeklyLabels,
            datasets: [{
                label: 'Calories Burned',
                data: chartData.weeklyCalories,
                backgroundColor: 'rgba(56, 161, 105, 0.7)',
                borderColor: '#38a169',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
});
