/**
 * API client for the Carbon Footprint Calculator
 */

// API base URL - using relative URL to work in both development and production
const API_BASE_URL = '';

/**
 * Makes a request to the API
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method
 * @param {object} data - Request body data for POST/PUT requests
 * @returns {Promise} - Response data
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

/**
 * API Functions
 */

// Calculate carbon footprint
async function calculateCarbonFootprint(formData) {
    return apiRequest('/calcular', 'POST', formData);
}

// Register a new property
async function registerProperty(propertyData) {
    return apiRequest('/cadastrar_propriedade', 'POST', propertyData);
}

// Calculate carbon credits potential
async function calculateCarbonCredits(data) {
    return apiRequest('/calcular-creditos', 'POST', data);
}

// Get property list
async function getProperties() {
    return apiRequest('/propriedades');
}

// Get property details by ID
async function getPropertyById(id) {
    return apiRequest(`/buscar_usuario/${id}`);
}
