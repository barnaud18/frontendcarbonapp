/**
 * Carbon Meter Visualization
 * Provides an animated visualization of carbon footprint results
 */

// Constants
const MAX_VALUE = 10000; // Maximum value for the meter (kg CO2e)
const ANIMATION_DURATION = 1000; // Animation duration in milliseconds

// Emission categories with their colors
const CATEGORIES = {
    'agricultura': { color: '#5cb85c', label: 'Agricultura' },
    'pecuaria': { color: '#d9534f', label: 'Pecuária' },
    'combustivel': { color: '#f0ad4e', label: 'Combustível' }
};

// Create the global carbonViz object with the public API
window.carbonViz = {
    initCarbonMeter,
    updateCarbonMeter,
    updateCategoryBreakdown
};

/**
 * Initialize the carbon meter visualization
 * Creates the SVG structure if it doesn't exist
 */
function initCarbonMeter() {
    console.log("Initializing carbon meter...");
    
    const meterContainer = document.getElementById('carbon-meter');
    if (!meterContainer) {
        console.error("Carbon meter container not found");
        return false;
    }
    
    // Clear any existing content
    meterContainer.innerHTML = '';
    
    // Create SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '300');
    svg.setAttribute('height', '200');
    svg.setAttribute('viewBox', '0 0 300 200');
    svg.classList.add('carbon-meter-svg');
    
    // Add meter elements to SVG
    const centerX = 150;
    const centerY = 150;
    const radius = 100;
    
    // Draw background arc (semicircle)
    const bgArc = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    bgArc.setAttribute('d', describeArc(centerX, centerY, radius, 180, 0));
    bgArc.setAttribute('fill', 'none');
    bgArc.setAttribute('stroke', '#333');
    bgArc.setAttribute('stroke-width', '10');
    svg.appendChild(bgArc);
    
    // Add colored sections
    const colorSections = [
        { color: '#28a745', startAngle: 180, endAngle: 135 }, // Low (green)
        { color: '#ffc107', startAngle: 135, endAngle: 90 },  // Medium (yellow)
        { color: '#fd7e14', startAngle: 90, endAngle: 45 },   // High (orange)
        { color: '#dc3545', startAngle: 45, endAngle: 0 }     // Very high (red)
    ];
    
    colorSections.forEach(section => {
        const arc = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        arc.setAttribute('d', describeArc(centerX, centerY, radius, section.startAngle, section.endAngle));
        arc.setAttribute('fill', 'none');
        arc.setAttribute('stroke', section.color);
        arc.setAttribute('stroke-width', '10');
        svg.appendChild(arc);
    });
    
    // Add tick marks & labels
    const ticks = [0, 45, 90, 135, 180];
    const labels = ["Extremo", "Alto", "Médio", "Baixo", "Mínimo"];
    
    ticks.forEach((angle, i) => {
        // Tick mark
        const innerRadius = radius - 15;
        const outerRadius = radius + 5;
        
        const x1 = centerX + innerRadius * Math.cos(angle * Math.PI / 180);
        const y1 = centerY + innerRadius * Math.sin(angle * Math.PI / 180);
        const x2 = centerX + outerRadius * Math.cos(angle * Math.PI / 180);
        const y2 = centerY + outerRadius * Math.sin(angle * Math.PI / 180);
        
        const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        tick.setAttribute('x1', x1);
        tick.setAttribute('y1', y1);
        tick.setAttribute('x2', x2);
        tick.setAttribute('y2', y2);
        tick.setAttribute('stroke', '#ccc');
        tick.setAttribute('stroke-width', '2');
        svg.appendChild(tick);
        
        // Label
        if (i % 2 === 0) { // Only show labels at 0, 90, 180 degrees
            const labelRadius = radius + 20;
            const labelX = centerX + labelRadius * Math.cos(angle * Math.PI / 180);
            const labelY = centerY + labelRadius * Math.sin(angle * Math.PI / 180);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', labelX);
            text.setAttribute('y', labelY);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', '#ccc');
            text.setAttribute('font-size', '10px');
            text.textContent = labels[i];
            svg.appendChild(text);
        }
    });
    
    // Add needle
    const needle = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    needle.setAttribute('id', 'carbon-meter-needle');
    needle.setAttribute('x1', centerX);
    needle.setAttribute('y1', centerY);
    needle.setAttribute('x2', centerX);
    needle.setAttribute('y2', centerY - radius);
    needle.setAttribute('stroke', '#fff');
    needle.setAttribute('stroke-width', '2');
    needle.setAttribute('transform', `rotate(180, ${centerX}, ${centerY})`);
    svg.appendChild(needle);
    
    // Add needle pivot circle
    const pivotCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    pivotCircle.setAttribute('cx', centerX);
    pivotCircle.setAttribute('cy', centerY);
    pivotCircle.setAttribute('r', '5');
    pivotCircle.setAttribute('fill', '#fff');
    svg.appendChild(pivotCircle);
    
    // Add value display
    const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    valueText.setAttribute('id', 'carbon-meter-value');
    valueText.setAttribute('x', centerX);
    valueText.setAttribute('y', centerY + 40);
    valueText.setAttribute('text-anchor', 'middle');
    valueText.setAttribute('fill', '#fff');
    valueText.setAttribute('font-weight', 'bold');
    valueText.textContent = '0 kg CO₂e';
    svg.appendChild(valueText);
    
    // Add SVG to container
    meterContainer.appendChild(svg);
    
    console.log("Carbon meter initialized successfully.");
    return true;
}

/**
 * Update the carbon meter to display a specific value
 * @param {number} value - Carbon footprint value in kg CO2e
 */
function updateCarbonMeter(value) {
    console.log("Updating carbon meter to:", value);
    
    const needle = document.getElementById('carbon-meter-needle');
    const valueText = document.getElementById('carbon-meter-value');
    
    if (!needle || !valueText) {
        console.error("Carbon meter elements not found");
        return false;
    }
    
    // Update value text immediately
    valueText.textContent = `${Math.round(value).toLocaleString()} kg CO₂e`;
    
    // Calculate angle based on value (180° at 0, 0° at MAX_VALUE)
    const clampedValue = Math.min(value, MAX_VALUE);
    const angle = 180 - (clampedValue / MAX_VALUE * 180);
    
    // Determine needle color based on value range
    let needleColor = '#28a745'; // Default: green
    
    if (angle < 45) {
        needleColor = '#dc3545'; // Red
    } else if (angle < 90) {
        needleColor = '#fd7e14'; // Orange
    } else if (angle < 135) {
        needleColor = '#ffc107'; // Yellow
    }
    
    // Set needle color
    needle.setAttribute('stroke', needleColor);
    
    // Animate needle rotation
    animateNeedle(needle, angle);
    
    return true;
}

/**
 * Update the category breakdown visualization
 * @param {object} details - Emission details by category
 */
function updateCategoryBreakdown(details) {
    const container = document.getElementById('carbon-breakdown');
    if (!container) {
        console.error("Carbon breakdown container not found");
        return false;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    // Calculate total emissions
    const total = Object.values(details).reduce((sum, val) => sum + val, 0);
    
    // Create category bars
    for (const [category, value] of Object.entries(details)) {
        if (!CATEGORIES[category]) continue;
        
        const percent = total > 0 ? (value / total * 100) : 0;
        
        // Create category container
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'carbon-category mb-2';
        
        // Add category header
        const header = document.createElement('div');
        header.className = 'd-flex justify-content-between';
        
        const nameSpan = document.createElement('span');
        nameSpan.textContent = CATEGORIES[category].label;
        
        const valueSpan = document.createElement('span');
        valueSpan.textContent = `${Math.round(value).toLocaleString()} kg CO₂e (${percent.toFixed(1)}%)`;
        
        header.appendChild(nameSpan);
        header.appendChild(valueSpan);
        categoryDiv.appendChild(header);
        
        // Add progress bar
        const progressDiv = document.createElement('div');
        progressDiv.className = 'progress mt-1';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar progress-bar-striped';
        progressBar.style.width = '0%'; // Start at 0 for animation
        progressBar.style.backgroundColor = CATEGORIES[category].color;
        progressBar.setAttribute('role', 'progressbar');
        
        progressDiv.appendChild(progressBar);
        categoryDiv.appendChild(progressDiv);
        
        // Add to container
        container.appendChild(categoryDiv);
        
        // Animate progress bar
        setTimeout(() => {
            progressBar.style.transition = 'width 1s ease-in-out';
            progressBar.style.width = `${percent}%`;
        }, 100);
    }
    
    return true;
}

/**
 * Helper function to animate needle rotation
 * @param {Element} needle - The SVG needle element
 * @param {number} targetAngle - Target angle in degrees
 */
function animateNeedle(needle, targetAngle) {
    const centerX = 150;
    const centerY = 150;
    
    // Get current angle from transform attribute
    let currentAngle = 180; // Default starting position
    const transform = needle.getAttribute('transform');
    
    if (transform && transform.includes('rotate')) {
        const match = transform.match(/rotate\(([^,]+)/);
        if (match && match[1]) {
            currentAngle = parseFloat(match[1]);
        }
    }
    
    // Animation variables
    const startTime = performance.now();
    const startAngle = currentAngle;
    const angleChange = targetAngle - startAngle;
    
    // Animation function
    function updateNeedle(timestamp) {
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / ANIMATION_DURATION, 1);
        
        // Easing function for smooth animation
        const easeProgress = easeOutQuad(progress);
        
        // Calculate current position
        const currentPosition = startAngle + angleChange * easeProgress;
        
        // Update needle position
        needle.setAttribute('transform', `rotate(${currentPosition}, ${centerX}, ${centerY})`);
        
        // Continue animation if not complete
        if (progress < 1) {
            requestAnimationFrame(updateNeedle);
        }
    }
    
    // Start animation
    requestAnimationFrame(updateNeedle);
}

/**
 * Easing function for smooth animation
 * @param {number} t - Progress value between 0 and 1
 * @returns {number} - Eased value
 */
function easeOutQuad(t) {
    return t * (2 - t);
}

/**
 * Helper function to create SVG arc path
 * @param {number} x - Center x coordinate
 * @param {number} y - Center y coordinate
 * @param {number} radius - Arc radius
 * @param {number} startAngle - Start angle in degrees
 * @param {number} endAngle - End angle in degrees
 * @returns {string} - SVG path description
 */
function describeArc(x, y, radius, startAngle, endAngle) {
    // Convert angles to radians
    const start = (startAngle - 90) * Math.PI / 180;
    const end = (endAngle - 90) * Math.PI / 180;
    
    // Calculate start and end points
    const startX = x + radius * Math.cos(start);
    const startY = y + radius * Math.sin(start);
    const endX = x + radius * Math.cos(end);
    const endY = y + radius * Math.sin(end);
    
    // Determine if the arc should be drawn the long way around
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    
    // Create path
    return [
        "M", startX, startY,
        "A", radius, radius, 0, largeArcFlag, 0, endX, endY
    ].join(" ");
}