/**
 * API communication module
 * Handles all interactions with the backend API
 */

// API base URL
const API_BASE = '/api';

/**
 * Makes a request to the API
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method
 * @param {object} data - Request body data for POST/PUT requests
 * @returns {Promise} - Response data
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE}${endpoint}`;
    
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        console.log(`Making API request to ${method} ${url}`);
        const response = await fetch(url, options);
        
        // Parse JSON response
        const contentType = response.headers.get('content-type');
        const responseData = contentType && contentType.includes('application/json') 
            ? await response.json() 
            : await response.text();
        
        if (!response.ok) {
            // Handle error response
            const error = new Error(responseData.message || responseData || 'API request failed');
            error.status = response.status;
            error.response = responseData;
            throw error;
        }
        
        return responseData;
    } catch (error) {
        console.error(`API request failed: ${error.message}`);
        throw error;
    }
}

/**
 * Calculates carbon footprint using the API
 * @param {object} formData - Form data with property details
 * @returns {Promise} - Calculation results
 */
async function apiCalculateFootprint(formData) {
    return await apiRequest('/calcular', 'POST', formData);
}

/**
 * Registers a new property with the API
 * @param {object} propertyData - Property data
 * @returns {Promise} - Registration results
 */
async function apiRegisterProperty(propertyData) {
    return await apiRequest('/cadastrar_propriedade', 'POST', propertyData);
}

/**
 * Calculates carbon credits potential
 * @param {object} data - Data for credit calculation
 * @returns {Promise} - Carbon credit results
 */
async function apiCalculateCredits(data) {
    return await apiRequest('/calcular', 'POST', data);
}

/**
 * Gets all registered properties
 * @returns {Promise} - List of properties
 */
async function getProperties() {
    return await apiRequest('/propriedades');
}

/**
 * Gets a property by ID
 * @param {number} id - Property ID
 * @returns {Promise} - Property data
 */
async function getPropertyById(id) {
    return await apiRequest(`/buscar_usuario/${id}`);
}