/**
 * Chart visualization module
 * Creates and updates Chart.js visualizations
 */

// Store chart instances for updates
let emissionsChart = null;
let reductionChart = null;

/**
 * Updates or creates the emissions by source chart
 * @param {object} detalhes - Emission details
 */
function updateEmissionsChart(detalhes) {
    const ctx = document.getElementById('emissaoPorFonte');
    
    if (!ctx) {
        console.error("Emissions chart canvas not found");
        return;
    }
    
    // Prepare data
    const labels = ['Agricultura', 'Pecuária', 'Combustível'];
    const data = [
        detalhes.agricultura,
        detalhes.pecuaria,
        detalhes.combustivel
    ];
    
    // Define colors with transparency
    const colors = [
        'rgba(92, 184, 92, 0.8)',  // Green for agriculture
        'rgba(217, 83, 79, 0.8)',  // Red for livestock
        'rgba(240, 173, 78, 0.8)'  // Yellow for fuel
    ];
    
    // Destroy existing chart if it exists
    if (emissionsChart) {
        emissionsChart.destroy();
    }
    
    // Create new chart
    emissionsChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ccc' // Light text for dark theme
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.chart.getDatasetMeta(0).total;
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${value.toLocaleString()} kg CO₂e (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Updates or creates the reduction potential chart
 * @param {array} recomendacoes - Recommendations with reduction potential
 */
function updateReductionChart(recomendacoes) {
    const ctx = document.getElementById('potencialReducao');
    
    if (!ctx) {
        console.error("Reduction chart canvas not found");
        return;
    }
    
    // Prepare data
    const labels = recomendacoes.map(rec => rec.acao);
    const data = recomendacoes.map(rec => rec.potencial_reducao);
    
    // Define gradient colors
    const colors = [
        'rgba(92, 184, 92, 0.8)',
        'rgba(2, 117, 216, 0.8)',
        'rgba(91, 192, 222, 0.8)',
        'rgba(240, 173, 78, 0.8)',
        'rgba(51, 122, 183, 0.8)'
    ];
    
    // Use a subset of colors if we have more recommendations than colors
    const backgroundColors = labels.map((_, i) => colors[i % colors.length]);
    
    // Destroy existing chart if it exists
    if (reductionChart) {
        reductionChart.destroy();
    }
    
    // Create new chart
    reductionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Potencial de Redução (kg CO₂e)',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Horizontal bar chart
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.toLocaleString()} kg CO₂e`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#ccc' // Light text for dark theme
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)' // Light grid lines
                    }
                },
                y: {
                    ticks: {
                        color: '#ccc' // Light text for dark theme
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}