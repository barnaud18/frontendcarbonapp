// Função para criar o gráfico de créditos de carbono
function criarGraficoCreditos(dadosGrafico, totalCreditos) {
    // Filtrar apenas metodologias com valores
    const labels = [];
    const values = [];
    
    if (dadosGrafico.pastagem > 0) {
        labels.push('Pastagem');
        values.push(dadosGrafico.pastagem);
    }
    if (dadosGrafico.florestal > 0) {
        labels.push('Florestal');
        values.push(dadosGrafico.florestal);
    }
    if (dadosGrafico.renovacao > 0) {
        labels.push('Renovação');
        values.push(dadosGrafico.renovacao);
    }
    if (dadosGrafico.integracao > 0) {
        labels.push('Integração');
        values.push(dadosGrafico.integracao);
    }
    
    // Configuração do gráfico
    const config = {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Créditos por Metodologia (tCO₂e)',
                data: values,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
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
                        color: '#fff'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const percentage = (value / totalCreditos * 100).toFixed(1);
                            return `${label}: ${value.toFixed(2)} tCO₂e (${percentage}%)`;
                        }
                    }
                }
            }
        }
    };
    
    // Renderizar o gráfico
    const ctx = document.getElementById('creditosChart').getContext('2d');
    return new Chart(ctx, config);
} 