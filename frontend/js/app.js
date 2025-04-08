/**
 * Main application logic for the Carbon Footprint Calculator
 */

// Store current property ID if a property is loaded
let currentPropertyId = null;

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Set up navigation
    setupNavigation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load properties for the property list page
    loadProperties();
});

/**
 * Sets up navigation between pages
 */
function setupNavigation() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const pages = document.querySelectorAll('.page');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target page ID from the href
            const targetId = this.getAttribute('href').substring(1);
            
            // Hide all pages
            pages.forEach(page => page.style.display = 'none');
            
            // Show the target page
            document.getElementById(targetId).style.display = 'block';
            
            // Update active nav link
            navLinks.forEach(navLink => navLink.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

/**
 * Sets up event listeners for forms and buttons
 */
function setupEventListeners() {
    // Calculate button
    document.getElementById('form-calculadora').addEventListener('submit', function(e) {
        e.preventDefault();
        calculateCarbonFootprint();
    });
    
    // Register property button
    document.getElementById('btn-cadastrar').addEventListener('click', function() {
        const formData = getFormData();
        apiRegisterProperty(formData);
    });
    
    // Calculate carbon credits button
    document.getElementById('btn-creditos').addEventListener('click', function() {
        calculateCarbonCredits();
    });
}

/**
 * Gets form data from the calculator form
 * @returns {object} Form data as an object
 */
function getFormData() {
    return {
        nome: document.getElementById('nome').value.trim(),
        tamanho_total: parseFloat(document.getElementById('tamanho_total').value) || 0,
        area_agricola: parseFloat(document.getElementById('area_agricola').value) || 0,
        uso_fertilizante: parseFloat(document.getElementById('uso_fertilizante').value) || 0,
        area_pastagem: parseFloat(document.getElementById('area_pastagem').value) || 0,
        num_bovinos: parseInt(document.getElementById('num_bovinos').value) || 0,
        consumo_combustivel: parseFloat(document.getElementById('consumo_combustivel').value) || 0
    };
}

/**
 * Calculates carbon footprint based on form data
 */
async function calculateCarbonFootprint() {
    try {
        // Get form data
        const formData = getFormData();
        
        // Add property ID if we're editing an existing property
        if (currentPropertyId) {
            formData.propriedade_id = currentPropertyId;
        }
        
        // Make API request
        const result = await apiCalculateFootprint(formData);
        
        // Display results
        displayResults(result);
        
        // Show success message
        showSuccess('Cálculo Realizado', 'A pegada de carbono foi calculada com sucesso.');
    } catch (error) {
        showError('Erro no Cálculo', error.message || 'Não foi possível calcular a pegada de carbono.');
    }
}

/**
 * Registers a new property
 * @param {object} formData - Form data object
 */
async function apiRegisterProperty(formData) {
    try {
        // Validate required fields
        if (!formData.nome) {
            throw new Error('O nome da propriedade é obrigatório.');
        }
        
        if (formData.tamanho_total <= 0) {
            throw new Error('O tamanho total da propriedade deve ser maior que zero.');
        }
        
        // Make API request
        const result = await apiRegisterProperty(formData);
        
        // Update current property ID
        currentPropertyId = result.propriedade_id;
        
        // Show success message
        showSuccess('Propriedade Cadastrada', `A propriedade "${formData.nome}" foi cadastrada com sucesso.`);
        
        // Reload properties list
        loadProperties();
    } catch (error) {
        showError('Erro no Cadastro', error.message || 'Não foi possível cadastrar a propriedade.');
    }
}

/**
 * Calculates carbon credits potential
 */
async function calculateCarbonCredits() {
    try {
        const areaPastagem = parseFloat(document.getElementById('area_pastagem').value) || 0;
        
        if (areaPastagem <= 0) {
            throw new Error('A área de pastagem deve ser maior que zero para calcular o potencial de créditos de carbono.');
        }
        
        // Make API request
        const result = await apiCalculateCredits({ area_pastagem: areaPastagem });
        
        // Display results
        const resultadoCreditos = document.getElementById('resultado-creditos');
        resultadoCreditos.innerHTML = `
            <div class="alert alert-success">
                <h5>Potencial de Créditos de Carbono</h5>
                <p><strong>Área de Pastagem:</strong> ${result.area_pastagem_ha} hectares</p>
                <p><strong>Potencial de Créditos:</strong> ${result.potencial_credito_tco2e} tCO₂e</p>
                <p><strong>Valor Estimado:</strong> R$ ${result.valor_estimado_reais.toFixed(2)}</p>
                <p class="mb-0"><small>*Baseado na metodologia VCS VM0032 para recuperação de pastagens degradadas.</small></p>
            </div>
        `;
    } catch (error) {
        showError('Erro no Cálculo', error.message || 'Não foi possível calcular os créditos de carbono.');
    }
}

/**
 * Loads the property list from the API
 */
async function loadProperties() {
    try {
        const properties = await getProperties();
        
        const tableBody = document.getElementById('tabela-propriedades');
        
        if (properties.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <div class="alert alert-info mb-0">
                            Nenhuma propriedade cadastrada. Use o formulário da calculadora para cadastrar uma nova propriedade.
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        tableBody.innerHTML = properties.map(prop => `
            <tr>
                <td>${prop.nome}</td>
                <td>${prop.tamanho_total} ha</td>
                <td>${new Date(prop.data_registro).toLocaleDateString('pt-BR')}</td>
                <td>${prop.emissao ? prop.emissao.total_emissao.toFixed(2) + ' kg CO₂e' : 'Não calculada'}</td>
                <td>
                    <button class="btn btn-sm btn-info property-button" data-id="${prop.id}">
                        Carregar
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Add event listeners to property buttons
        setupPropertyButtons();
    } catch (error) {
        showError('Erro ao Carregar Propriedades', error.message || 'Não foi possível carregar a lista de propriedades.');
    }
}

/**
 * Sets up event listeners for property buttons
 */
function setupPropertyButtons() {
    const buttons = document.querySelectorAll('.property-button');
    
    buttons.forEach(button => {
        button.addEventListener('click', async function() {
            const propertyId = this.getAttribute('data-id');
            
            try {
                const property = await getPropertyById(propertyId);
                
                // Fill the form with property data
                fillPropertyForm(property);
                
                // Update current property ID
                currentPropertyId = property.id;
                
                // Switch to calculator page
                document.querySelector('.nav-link[href="#calculadora"]').click();
                
                // Show success message
                showSuccess('Propriedade Carregada', `A propriedade "${property.nome}" foi carregada com sucesso.`);
                
                // If property has emissions calculated, display results
                if (property.emissao) {
                    displayResults({
                        pegada_total_kg_co2e: property.emissao.total_emissao,
                        detalhes: {
                            agricultura: property.emissao.emissao_agricultura,
                            pecuaria: property.emissao.emissao_pecuaria,
                            combustivel: property.emissao.emissao_combustivel
                        },
                        potencial_credito_tco2e: property.emissao.potencial_credito,
                        recomendacoes: property.recomendacoes
                    });
                }
            } catch (error) {
                showError('Erro ao Carregar Propriedade', error.message || 'Não foi possível carregar os dados da propriedade.');
            }
        });
    });
}

/**
 * Fills the form with property data
 * @param {object} property - Property data object
 */
function fillPropertyForm(property) {
    document.getElementById('nome').value = property.nome;
    document.getElementById('tamanho_total').value = property.tamanho_total;
    
    if (property.agricultura) {
        document.getElementById('area_agricola').value = property.agricultura.area_agricola;
        document.getElementById('uso_fertilizante').value = property.agricultura.uso_fertilizante;
        document.getElementById('area_pastagem').value = property.agricultura.area_pastagem;
        document.getElementById('consumo_combustivel').value = property.agricultura.consumo_combustivel;
    }
    
    if (property.pecuaria) {
        document.getElementById('num_bovinos').value = property.pecuaria.num_bovinos;
    }
}

/**
 * Displays calculation results
 * @param {object} data - Result data from API
 */
function displayResults(data) {
    const resultadoContainer = document.getElementById('resultado-container');
    
    // Format numbers for display
    const pegadaTotal = data.pegada_total_kg_co2e.toFixed(2);
    const emissaoAgricultura = data.detalhes.agricultura.toFixed(2);
    const emissaoPecuaria = data.detalhes.pecuaria.toFixed(2);
    const emissaoCombustivel = data.detalhes.combustivel.toFixed(2);
    const potencialCredito = data.potencial_credito_tco2e.toFixed(2);
    
    // Create recommendations HTML
    const recomendacoesHTML = data.recomendacoes.map(rec => `
        <div class="alert alert-info">
            <h6>${rec.acao}</h6>
            <p>${rec.descricao || ''}</p>
            <p class="mb-0"><strong>Redução estimada:</strong> ${rec.potencial_reducao.toFixed(2)} kg CO₂e</p>
        </div>
    `).join('');
    
    // Update the results container
    resultadoContainer.innerHTML = `
        <div class="card mb-3">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Pegada de Carbono Total</h5>
            </div>
            <div class="card-body text-center">
                <h2 class="display-4">${pegadaTotal} kg CO₂e</h2>
                <p>Potencial de Créditos de Carbono: ${potencialCredito} tCO₂e</p>
            </div>
        </div>
        
        <h5>Detalhes por Fonte de Emissão</h5>
        <table class="table table-bordered">
            <thead class="table-light">
                <tr>
                    <th>Fonte</th>
                    <th>Emissões (kg CO₂e)</th>
                    <th>% do Total</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Agricultura</td>
                    <td>${emissaoAgricultura}</td>
                    <td>${((data.detalhes.agricultura / data.pegada_total_kg_co2e) * 100).toFixed(1)}%</td>
                </tr>
                <tr>
                    <td>Pecuária</td>
                    <td>${emissaoPecuaria}</td>
                    <td>${((data.detalhes.pecuaria / data.pegada_total_kg_co2e) * 100).toFixed(1)}%</td>
                </tr>
                <tr>
                    <td>Combustível</td>
                    <td>${emissaoCombustivel}</td>
                    <td>${((data.detalhes.combustivel / data.pegada_total_kg_co2e) * 100).toFixed(1)}%</td>
                </tr>
            </tbody>
        </table>
        
        <h5 class="mt-4">Recomendações para Mitigação</h5>
        ${recomendacoesHTML}
    `;
    
    // Update charts
    updateEmissionsChart(data.detalhes);
    updateReductionChart(data.recomendacoes);
}

/**
 * Shows a success alert
 * @param {string} title - Alert title
 * @param {string} message - Alert message
 */
function showSuccess(title, message) {
    const alertsContainer = document.getElementById('alerts');
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        <h5>${title}</h5>
        <p class="mb-0">${message}</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

/**
 * Shows an error alert
 * @param {string} title - Alert title
 * @param {string} message - Alert message
 */
function showError(title, message) {
    const alertsContainer = document.getElementById('alerts');
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <h5>${title}</h5>
        <p class="mb-0">${message}</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 8 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 8000);
}
