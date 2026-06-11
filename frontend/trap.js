// =============================
// AI Trap Frontend Logic
// =============================

console.log(' trap.js loaded');

let selectedImageFile = null;
let selectedFormat = 'json';

// =============================
// Initialize Trap Page
// =============================

document.addEventListener('DOMContentLoaded', function () {
    console.log(' Initializing AI Trap page...');
    initTrapPage();
});

function initTrapPage() {
    // Dropzone
    const dropzone = document.getElementById('trap-dropzone');
    const input = document.getElementById('trap-input');

    dropzone.addEventListener('click', () => input.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleImageSelect(e.dataTransfer.files[0]);
        }
    });

    input.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleImageSelect(e.target.files[0]);
        }
    });

    // Sliders
    const variantsSlider = document.getElementById('trap-variants');
    const intensitySlider = document.getElementById('trap-intensity');

    variantsSlider.addEventListener('input', (e) => {
        document.getElementById('trap-variants-label').textContent = e.target.value;
        resetMetrics(); // Clear metrics when slider changes
    });

    intensitySlider.addEventListener('input', (e) => {
        const value = e.target.value;
        let label = value;
        if (value < 25) label += ' (Subtle)';
        else if (value < 75) label += ' (Balanced)';
        else label += ' (Aggressive)';
        document.getElementById('trap-intensity-label').textContent = label;
        resetMetrics(); // Clear metrics when slider changes
    });

    // Format buttons
    document.querySelectorAll('.format-btn').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedFormat = btn.dataset.format;
            console.log(' Format selected:', selectedFormat);
        });
    });

    // Generate button
    document.getElementById('trap-btn').addEventListener('click', generateTrap);

    // Quick analysis button
    document.getElementById('trap-analyze-btn').addEventListener('click', quickAnalysis);

    // Download button
    document.getElementById('trap-download-btn').addEventListener('click', downloadTrap);

    console.log(' AI Trap page initialized');
}

// =============================
// Image Selection
// =============================

function handleImageSelect(file) {
    console.log(' Image selected:', file.name);

    // Validate
    if (!file.type.startsWith('image/')) {
        showNotification('Please select a valid image file', 'error');
        return;
    }

    selectedImageFile = file;

    // Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('trap-preview');
        const placeholder = document.getElementById('trap-placeholder');

        preview.src = e.target.result;
        preview.style.display = 'block';
        placeholder.style.display = 'none';

        console.log(' Image preview loaded');
    };
    reader.readAsDataURL(file);

    // Enable buttons
    document.getElementById('trap-btn').disabled = false;
    document.getElementById('trap-analyze-btn').disabled = false;

    showNotification(`Image ready: ${file.name}`, 'info');
}

// =============================
// Quick Analysis
// =============================

async function quickAnalysis() {
    if (!selectedImageFile) {
        showNotification('Please select an image first', 'error');
        return;
    }

    console.log(' Starting quick analysis...');

    const btn = document.getElementById('trap-analyze-btn');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-spinner"></span> Analyzing...';

    try {
        const formData = new FormData();
        formData.append('file', selectedImageFile);

        const response = await fetch(`${API_BASE}/trap/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const result = await response.json();

        console.log(' Analysis complete:', result);

        // Display results
        const score = Math.round(result.poison_potential_score);
        const recommendation = result.recommendation;

        const message = `Score: ${score}/100 - ${recommendation}`;
        const type = score > 40 ? 'success' : score > 20 ? 'info' : 'error';

        showNotification(message, type);

        // Suggest intensity
        if (score < 20) {
            showNotification(' Try increasing intensity to 75 for better results', 'info');
        }
    } catch (error) {
        console.error(' Analysis failed:', error);
        showNotification(`Analysis error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// =============================
// Generate Trap
// =============================

async function generateTrap() {
    if (!selectedImageFile) {
        showNotification('Please select an image first', 'error');
        return;
    }

    console.log(' Starting trap generation...');

    const btn = document.getElementById('trap-btn');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-spinner"></span> Generating...';

    const variants = parseInt(document.getElementById('trap-variants').value);
    const intensity = parseInt(document.getElementById('trap-intensity').value);

    try {
        const formData = new FormData();
        formData.append('file', selectedImageFile);
        formData.append('variants', variants);
        formData.append('intensity', intensity);
        formData.append('format', selectedFormat);

        console.log(`Generating ${variants} variants at intensity ${intensity}`);

        updateStatus('generating', `Generating ${variants} variants (this may take 30s)...`);

        const response = await fetch(`${API_BASE}/trap/generate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        if (selectedFormat === 'zip') {
            // Handle ZIP download
            const blob = await response.blob();
            window.trapPackageBlob = blob;

            updateStatus('success', ' Trap package generated! Ready to download.');
            document.getElementById('trap-download-btn').disabled = false;

            console.log(' ZIP package ready, size:', blob.size, 'bytes');
            showNotification('Trap package generated! Click download to save.', 'success');
        } else {
            // Handle JSON response
            const result = await response.json();

            window.trapPackageJSON = result;

            // Display metrics
            displayMetrics(result);

            updateStatus('success', ' Trap package generated! Ready to download.');
            document.getElementById('trap-download-btn').disabled = false;

            console.log(' JSON package ready with', result.poisoned_images.length, 'variants');
            showNotification(`Generated ${result.poisoned_images.length} poisoned variants!`, 'success');
        }
    } catch (error) {
        console.error(' Generation failed:', error);
        updateStatus('error', ` Error: ${error.message}`);
        showNotification(`Generation error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// =============================
// Display Metrics
// =============================

function displayMetrics(result) {
    console.log(' Displaying metrics:', result.summary);

    const score = result.poison_strength_score;
    const summary = result.summary;

    // Poison Score with bar
    document.getElementById('trap-score').textContent = score.toFixed(1);
    const barWidth = (score / 100) * 100;
    document.getElementById('trap-score-bar').style.width = barWidth + '%';
    document.getElementById('trap-score-bar').style.background = getScoreColor(score);

    // Other metrics
    document.getElementById('trap-drift').textContent = summary.avg_embedding_drift.toFixed(2) + '%';
    document.getElementById('trap-conf').textContent = summary.avg_confidence_drop.toFixed(1) + '%';
    document.getElementById('trap-variant-count').textContent = summary.num_variants;
}

function resetMetrics() {
    // Reset all metrics to "–" when sliders change
    document.getElementById('trap-score').textContent = '–';
    document.getElementById('trap-score-bar').style.width = '0%';
    document.getElementById('trap-score-bar').style.background = '#666';
    document.getElementById('trap-drift').textContent = '–';
    document.getElementById('trap-conf').textContent = '–';
    document.getElementById('trap-variant-count').textContent = '–';
    updateStatus('idle', 'Adjust parameters and generate to see new metrics.');
}

function getScoreColor(score) {
    if (score > 60) return 'linear-gradient(90deg, #22c55e, #10b981)';
    if (score > 40) return 'linear-gradient(90deg, #f59e0b, #f97316)';
    if (score > 20) return 'linear-gradient(90deg, #eab308, #f59e0b)';
    return 'linear-gradient(90deg, #ef4444, #dc2626)';
}

function updateStatus(status, message) {
    const statusEl = document.getElementById('trap-status');
    statusEl.textContent = message;
    statusEl.className = `status-pill status-${status}`;
}

// =============================
// Download Package
// =============================

function downloadTrap() {
    console.log('⬇️ Downloading trap package...');

    if (selectedFormat === 'zip') {
        if (!window.trapPackageBlob) {
            showNotification('No package available', 'error');
            return;
        }

        const url = URL.createObjectURL(window.trapPackageBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trap_${new Date().getTime()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log(' ZIP package downloaded');
        showNotification('ZIP package downloaded!', 'success');
    } else {
        if (!window.trapPackageJSON) {
            showNotification('No package available', 'error');
            return;
        }

        // Create JSON file with metadata (images excluded for size)
        const dataToDownload = {
            poison_strength_score: window.trapPackageJSON.poison_strength_score,
            summary: window.trapPackageJSON.summary,
            metadata: window.trapPackageJSON.metadata,
            image_count: window.trapPackageJSON.poisoned_images.length,
            download_note: 'Full poisoned images are base64 encoded in the original response. ' +
                'For ZIP with all files, regenerate with format=zip.'
        };

        const jsonString = JSON.stringify(dataToDownload, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trap_metadata_${new Date().getTime()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log(' JSON metadata downloaded');
        showNotification('Metadata downloaded! For full package with images, use ZIP format.', 'info');
    }
}

// =============================
// Utilities
// =============================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `main-notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

console.log(' AI Trap frontend initialized');
