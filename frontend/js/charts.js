/**
 * Chart functions for the Carbon Footprint Calculator
 */

// Store chart instances to update them later
let emissionsChart = null;
let reductionChart = null;

/**
 * Updates or creates the emissions by source chart
 * @param {object} detalhes - Emission details
 */
function updateEmissionsChart(detalhes) {
    const ctx = document.getElementById('emissaoPorFonte');
    
    // Prepare data
    const labels = ['Agricultura', 'Pecuária', 'Combustível'];
    const data = [
        detalhes.agricultura || 0,
        detalhes.pecuaria || 0,
        detalhes.combustivel || 0
    ];
    
    // Calculate percentages for labels
    const total = data.reduce((sum, value) => sum + value, 0);
    const percentages = data.map(value => ((value / total) * 100).toFixed(1));
    
    const labelWithPercentages = labels.map((label, index) => {
        return `${label} (${percentages[index]}%)`;
    });
    
    // Set colors
    const backgroundColor = [
        'rgba(75, 192, 192, 0.8)',  // Teal for Agriculture
        'rgba(255, 159, 64, 0.8)',  // Orange for Livestock
        'rgba(153, 102, 255, 0.8)'  // Purple for Fuel
    ];
    
    const chartConfig = {
        type: 'pie',
        data: {
            labels: labelWithPercentages,
            datasets: [{
                data: data,
                backgroundColor: backgroundColor,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Distribuição de Emissões por Fonte'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label.split(' (')[0]}: ${value.toFixed(2)} kg CO₂e (${percentage}%)`;
                        }
                    }
                }
            }
        }
    };
    
    // Destroy existing chart if it exists
    if (emissionsChart) {
        emissionsChart.destroy();
    }
    
    // Create new chart
    emissionsChart = new Chart(ctx, chartConfig);
}

/**
 * Updates or creates the reduction potential chart
 * @param {array} recomendacoes - Recommendations with reduction potential
 */
function updateReductionChart(recomendacoes) {
    const ctx = document.getElementById('potencialReducao');
    
    // Prepare data
    const labels = recomendacoes.map(rec => rec.acao);
    const data = recomendacoes.map(rec => rec.potencial_reducao);
    
    // Set colors
    const backgroundColor = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(153, 102, 255, 0.7)'
    ];
    
    const chartConfig = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Potencial de Redução (kg CO₂e)',
                data: data,
                backgroundColor: backgroundColor,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Potencial de Redução por Ação'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'kg CO₂e'
                    }
                }
            }
        }
    };
    
    // Destroy existing chart if it exists
    if (reductionChart) {
        reductionChart.destroy();
    }
    
    // Create new chart
    reductionChart = new Chart(ctx, chartConfig);
}
