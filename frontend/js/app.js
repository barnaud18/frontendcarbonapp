/**
 * Main application logic for the Carbon Footprint Calculator
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded - initializing application");
    
    // Set up event listeners
    setupEventListeners();
    
    // Set up navigation
    setupNavigation();
    
    // Try to initialize carbon meter if it exists
    if (window.carbonViz && typeof window.carbonViz.initCarbonMeter === 'function') {
        window.carbonViz.initCarbonMeter();
        console.log("Carbon meter initialized");
    } else {
        console.warn("Carbon visualization not available");
    }
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
    console.log("Setting up event listeners");
    
    // Calculate button
    const calcButton = document.getElementById('btn-calcular');
    if (calcButton) {
        calcButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Calculate button clicked");
            calculateCarbonFootprint();
        });
    }
    
    // Register property button
    const cadastrarButton = document.getElementById('btn-cadastrar');
    if (cadastrarButton) {
        cadastrarButton.addEventListener('click', function() {
            console.log("Register property button clicked");
            const formData = getFormData();
            registerProperty(formData);
        });
    }
    
    // Calculate carbon credits button
    const creditosButton = document.getElementById('btn-creditos');
    if (creditosButton) {
        creditosButton.addEventListener('click', function() {
            console.log("Calculate credits button clicked");
            calculateCarbonCredits();
        });
    }
}

/**
 * Gets form data from the calculator form
 * @returns {object} Form data as an object
 */
function getFormData() {
    return {
        nome: document.getElementById('nome').value.trim() || "Propriedade Teste",
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
        console.log("Calculating carbon footprint...");
        
        // Get form data
        const formData = getFormData();
        console.log("Form data:", formData);
        
        // Make API request
        const result = await apiCalculateFootprint(formData);
        console.log("Calculation result:", result);
        
        // Display results
        displayResults(result);
        
        // Show success message
        showSuccess('Cálculo Realizado', 'A pegada de carbono foi calculada com sucesso.');
    } catch (error) {
        console.error("Error calculating footprint:", error);
        showError('Erro no Cálculo', error.message || 'Não foi possível calcular a pegada de carbono.');
    }
}

/**
 * Registers a new property
 * @param {object} formData - Form data object
 */
async function registerProperty(formData) {
    try {
        // Validate required fields
        if (!formData.nome) {
            throw new Error('O nome da propriedade é obrigatório.');
        }
        
        console.log("Registering property:", formData);
        
        // Make API request
        const result = await apiRegisterProperty(formData);
        console.log("Registration result:", result);
        
        // Show success message
        showSuccess('Propriedade Cadastrada', `A propriedade "${formData.nome}" foi cadastrada com sucesso.`);
    } catch (error) {
        console.error("Error registering property:", error);
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
        
        console.log("Calculating carbon credits for area:", areaPastagem);
        
        // Make API request
        const result = await apiCalculateCredits({ area_pastagem: areaPastagem });
        console.log("Credits calculation result:", result);
        
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
        console.error("Error calculating credits:", error);
        showError('Erro no Cálculo', error.message || 'Não foi possível calcular os créditos de carbono.');
    }
}

/**
 * Displays calculation results
 * @param {object} data - Result data from API
 */
function displayResults(data) {
    console.log("Displaying results:", data);
    
    const resultadoContainer = document.getElementById('resultado-container');
    
    // Update the results container with simplified HTML
    resultadoContainer.innerHTML = `
        <div class="card mb-3">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Pegada de Carbono Total</h5>
            </div>
            <div class="card-body text-center">
                <h2 class="display-4">${data.pegada_total_kg_co2e.toFixed(2)} kg CO₂e</h2>
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
                    <td>${data.detalhes.agricultura.toFixed(2)}</td>
                    <td>${((data.detalhes.agricultura / data.pegada_total_kg_co2e) * 100).toFixed(1)}%</td>
                </tr>
                <tr>
                    <td>Pecuária</td>
                    <td>${data.detalhes.pecuaria.toFixed(2)}</td>
                    <td>${((data.detalhes.pecuaria / data.pegada_total_kg_co2e) * 100).toFixed(1)}%</td>
                </tr>
                <tr>
                    <td>Combustível</td>
                    <td>${data.detalhes.combustivel.toFixed(2)}</td>
                    <td>${((data.detalhes.combustivel / data.pegada_total_kg_co2e) * 100).toFixed(1)}%</td>
                </tr>
            </tbody>
        </table>
    `;
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