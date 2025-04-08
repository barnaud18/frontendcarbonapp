/**
 * Carbon Meter Visualization
 * Provides an animated visualization of carbon footprint results
 */

// Store reference to the carbon meter element and its components
let carbonMeter = null;
let carbonMeterValue = null;
let carbonMeterNeedle = null;
let carbonMeterScale = null;

// Store animation properties
let targetValue = 0;
let currentValue = 0;
let animationFrameId = null;

// Carbon footprint categories and their colors
const categories = {
    'agricultura': { color: '#5cb85c', label: 'Agricultura' },
    'pecuaria': { color: '#d9534f', label: 'Pecuária' },
    'combustivel': { color: '#f0ad4e', label: 'Combustível' }
};

/**
 * Initialize the carbon meter visualization
 */
function initCarbonMeter() {
    // Find carbon meter elements
    carbonMeter = document.getElementById('carbon-meter');
    
    if (!carbonMeter) {
        console.error('Carbon meter element not found');
        return;
    }
    
    // Create the carbon meter SVG container if it doesn't exist
    if (carbonMeter.querySelector('svg') === null) {
        createCarbonMeterSVG();
    }
    
    // Get references to meter components
    carbonMeterValue = document.getElementById('carbon-meter-value');
    carbonMeterNeedle = document.getElementById('carbon-meter-needle');
    carbonMeterScale = document.getElementById('carbon-meter-scale');
    
    // Set initial states
    updateCarbonMeterValue(0);
}

/**
 * Create the SVG elements for the carbon meter
 */
function createCarbonMeterSVG() {
    // Constants for meter dimensions
    const width = 300;
    const height = 200;
    const radius = 120;
    const centerX = width / 2;
    const centerY = height - 20; // Position at bottom of container
    
    // Create SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('class', 'carbon-meter-svg');
    
    // Create gauge background (semi-circle)
    const background = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const startAngle = Math.PI;
    const endAngle = 0;
    
    const x1 = centerX + radius * Math.cos(startAngle);
    const y1 = centerY + radius * Math.sin(startAngle);
    const x2 = centerX + radius * Math.cos(endAngle);
    const y2 = centerY + radius * Math.sin(endAngle);
    
    const largeArcFlag = Math.abs(endAngle - startAngle) > Math.PI ? 1 : 0;
    
    const d = [
        'M', x1, y1,
        'A', radius, radius, 0, largeArcFlag, 1, x2, y2
    ].join(' ');
    
    background.setAttribute('d', d);
    background.setAttribute('fill', 'none');
    background.setAttribute('stroke', '#444');
    background.setAttribute('stroke-width', '2');
    
    // Create gauge scale
    const scale = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    scale.setAttribute('id', 'carbon-meter-scale');
    
    // Create colored sections for different impact levels
    const sections = [
        { color: '#28a745', endAngle: Math.PI * 5/6 },    // Low impact (green)
        { color: '#ffc107', endAngle: Math.PI * 2/3 },    // Medium impact (yellow)
        { color: '#fd7e14', endAngle: Math.PI * 1/3 },    // High impact (orange)
        { color: '#dc3545', endAngle: 0 }                 // Very high impact (red)
    ];
    
    sections.forEach((section, index) => {
        const startAng = index === 0 ? Math.PI : sections[index-1].endAngle;
        const endAng = section.endAngle;
        
        const x1 = centerX + radius * Math.cos(startAng);
        const y1 = centerY + radius * Math.sin(startAng);
        const x2 = centerX + radius * Math.cos(endAng);
        const y2 = centerY + radius * Math.sin(endAng);
        
        const largeArcFlag = Math.abs(endAng - startAng) > Math.PI ? 1 : 0;
        
        const d = [
            'M', x1, y1,
            'A', radius, radius, 0, largeArcFlag, 1, x2, y2
        ].join(' ');
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', section.color);
        path.setAttribute('stroke-width', '8');
        
        scale.appendChild(path);
    });
    
    // Add tick marks
    const tickCount = 5;
    const tickLength = 10;
    
    for (let i = 0; i <= tickCount; i++) {
        const angle = Math.PI - (Math.PI * i / tickCount);
        
        const innerX = centerX + (radius - tickLength) * Math.cos(angle);
        const innerY = centerY + (radius - tickLength) * Math.sin(angle);
        const outerX = centerX + radius * Math.cos(angle);
        const outerY = centerY + radius * Math.sin(angle);
        
        const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        tick.setAttribute('x1', innerX);
        tick.setAttribute('y1', innerY);
        tick.setAttribute('x2', outerX);
        tick.setAttribute('y2', outerY);
        tick.setAttribute('stroke', '#ccc');
        tick.setAttribute('stroke-width', '2');
        
        scale.appendChild(tick);
        
        // Add labels for first, middle, and last tick
        if (i === 0 || i === Math.floor(tickCount / 2) || i === tickCount) {
            const labelX = centerX + (radius + 15) * Math.cos(angle);
            const labelY = centerY + (radius + 15) * Math.sin(angle);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', labelX);
            text.setAttribute('y', labelY);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#ccc');
            text.setAttribute('font-size', '12px');
            
            let label = '';
            if (i === 0) label = 'Alto';
            else if (i === Math.floor(tickCount / 2)) label = 'Médio';
            else if (i === tickCount) label = 'Baixo';
            
            text.textContent = label;
            
            scale.appendChild(text);
        }
    }
    
    // Create needle
    const needle = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    needle.setAttribute('id', 'carbon-meter-needle');
    needle.setAttribute('x1', centerX);
    needle.setAttribute('y1', centerY);
    needle.setAttribute('x2', centerX);
    needle.setAttribute('y2', centerY - radius);
    needle.setAttribute('stroke', '#fff');
    needle.setAttribute('stroke-width', '2');
    needle.setAttribute('transform', `rotate(180, ${centerX}, ${centerY})`); // Start at bottom (low)
    
    // Create needle circle
    const needleCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    needleCircle.setAttribute('cx', centerX);
    needleCircle.setAttribute('cy', centerY);
    needleCircle.setAttribute('r', '6');
    needleCircle.setAttribute('fill', '#fff');
    
    // Create value text
    const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    valueText.setAttribute('id', 'carbon-meter-value');
    valueText.setAttribute('x', centerX);
    valueText.setAttribute('y', centerY + 30);
    valueText.setAttribute('text-anchor', 'middle');
    valueText.setAttribute('font-size', '16px');
    valueText.setAttribute('font-weight', 'bold');
    valueText.setAttribute('fill', '#fff');
    valueText.textContent = '0 kg CO₂e';
    
    // Add all elements to SVG
    svg.appendChild(background);
    svg.appendChild(scale);
    svg.appendChild(needle);
    svg.appendChild(needleCircle);
    svg.appendChild(valueText);
    
    // Add SVG to carbon meter container
    carbonMeter.appendChild(svg);
}

/**
 * Update the carbon meter to display a new value
 * @param {number} value - Carbon footprint value in kg CO2e
 * @param {boolean} animate - Whether to animate the update
 */
function updateCarbonMeter(value, animate = true) {
    // Cancel any existing animation
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    
    // Set target value
    targetValue = value;
    
    // Update immediately if no animation
    if (!animate) {
        currentValue = targetValue;
        updateCarbonMeterValue(currentValue);
        return;
    }
    
    // Start animation
    animateCarbonMeter();
}

/**
 * Animate the carbon meter to the target value
 */
function animateCarbonMeter() {
    // Calculate step based on difference
    const diff = targetValue - currentValue;
    const step = diff * 0.1; // Move 10% of the distance each frame
    
    // Update current value
    if (Math.abs(diff) < 1) {
        currentValue = targetValue;
    } else {
        currentValue += step;
    }
    
    // Update meter display
    updateCarbonMeterValue(currentValue);
    
    // Continue animation if not reached target
    if (currentValue !== targetValue) {
        animationFrameId = requestAnimationFrame(animateCarbonMeter);
    } else {
        animationFrameId = null;
    }
}

/**
 * Update the visual elements of the carbon meter
 * @param {number} value - Current carbon footprint value
 */
function updateCarbonMeterValue(value) {
    if (!carbonMeterValue || !carbonMeterNeedle) return;
    
    // Update value text
    carbonMeterValue.textContent = `${Math.round(value).toLocaleString()} kg CO₂e`;
    
    // Map value to angle (0 to 10000 kg CO2e maps to 180° to 0°)
    // Clamp max value to 10000 for display purposes
    const clampedValue = Math.min(value, 10000);
    const angle = 180 - (clampedValue / 10000 * 180);
    
    // Update needle rotation
    carbonMeterNeedle.setAttribute('transform', `rotate(${angle}, 150, 180)`);
    
    // Update color based on angle
    let needleColor = '#28a745'; // Default green
    
    if (angle < 45) {
        needleColor = '#dc3545'; // Red - very high
    } else if (angle < 90) {
        needleColor = '#fd7e14'; // Orange - high
    } else if (angle < 135) {
        needleColor = '#ffc107'; // Yellow - medium
    }
    
    carbonMeterNeedle.setAttribute('stroke', needleColor);
}

/**
 * Create or update the category breakdown chart
 * @param {object} details - Emission details by category
 */
function updateCategoryBreakdown(details) {
    const container = document.getElementById('carbon-breakdown');
    if (!container) return;
    
    // Clear container
    container.innerHTML = '';
    
    // Calculate total
    const total = Object.values(details).reduce((sum, val) => sum + val, 0);
    
    // Create category bars
    Object.entries(details).forEach(([category, value]) => {
        if (!categories[category]) return;
        
        const percent = total > 0 ? (value / total * 100) : 0;
        
        // Create category container
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'carbon-category mb-2';
        
        // Create label
        const label = document.createElement('div');
        label.className = 'd-flex justify-content-between mb-1';
        
        const nameSpan = document.createElement('span');
        nameSpan.textContent = categories[category].label;
        
        const valueSpan = document.createElement('span');
        valueSpan.textContent = `${Math.round(value).toLocaleString()} kg CO₂e (${percent.toFixed(1)}%)`;
        
        label.appendChild(nameSpan);
        label.appendChild(valueSpan);
        
        // Create progress bar
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
        progressBar.style.width = `${percent}%`;
        progressBar.style.backgroundColor = categories[category].color;
        progressBar.setAttribute('role', 'progressbar');
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.setAttribute('aria-valuemin', '0');
        progressBar.setAttribute('aria-valuemax', '100');
        
        progressContainer.appendChild(progressBar);
        
        // Add elements to category container
        categoryDiv.appendChild(label);
        categoryDiv.appendChild(progressContainer);
        
        // Add category to main container
        container.appendChild(categoryDiv);
    });
}

// Export functions
window.carbonViz = {
    initCarbonMeter,
    updateCarbonMeter,
    updateCategoryBreakdown
};