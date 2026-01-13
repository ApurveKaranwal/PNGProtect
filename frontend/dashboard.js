// Dashboard JavaScript functionality
// API_BASE is already declared globally in script.js
let currentUser = null;
let authToken = localStorage.getItem('pngprotect_token');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
  console.log('Dashboard initializing...');
  console.log('Auth token:', authToken ? 'Present' : 'Missing');
  
  if (!authToken) {
    console.log('No auth token, redirecting to login');
    window.location.href = 'login.html';
    return;
  }

  try {
    await loadUserInfo();
    await loadDashboardData();
    setupEventListeners();
    setupNavigationAlignment();
    
    // Initialize particles if the function exists
    if (typeof initParticles === 'function') {
      initParticles();
    } else {
      console.log('initParticles function not found, skipping particle animation');
    }
  } catch (error) {
    console.error('Dashboard initialization failed:', error);
    showNotification('Failed to load dashboard. Please try logging in again.', 'error');
    setTimeout(() => {
      localStorage.removeItem('pngprotect_token');
      window.location.href = 'login.html';
    }, 3000);
  }
});

// Setup navigation alignment
function setupNavigationAlignment() {
  const navLinks = document.querySelectorAll('.nav-links a');
  const sections = document.querySelectorAll('.dashboard-section');
  
  // Handle navigation clicks
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href.startsWith('#')) {
        e.preventDefault();
        
        // Update active state
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        // Show corresponding section
        const targetId = href.substring(1);
        sections.forEach(section => {
          if (section.id === targetId) {
            section.style.display = 'block';
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
          } else {
            section.style.display = 'none';
          }
        });
      }
    });
  });
  
  // Show dashboard section by default
  sections.forEach(section => {
    section.style.display = section.id === 'dashboard' ? 'block' : 'none';
  });
}

// Load user information
async function loadUserInfo() {
  console.log('Loading user info...');
  try {
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    console.log('User info response status:', response.status);

    if (response.ok) {
      currentUser = await response.json();
      console.log('User loaded:', currentUser.full_name);
      document.getElementById('user-name').textContent = currentUser.full_name;
    } else {
      throw new Error(`Authentication failed: ${response.status}`);
    }
  } catch (error) {
    console.error('Failed to load user info:', error);
    localStorage.removeItem('pngprotect_token');
    throw error;
  }
}

// Load dashboard data
async function loadDashboardData() {
  try {
    await Promise.all([
      loadDashboardStats(),
      loadTemplates(),
      loadAnalytics()
    ]);
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    showNotification('Failed to load dashboard data', 'error');
  }
}

// Load dashboard statistics
async function loadDashboardStats() {
  console.log('Loading dashboard stats...');
  try {
    const response = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    console.log('Dashboard stats response status:', response.status);

    if (response.ok) {
      const stats = await response.json();
      console.log('Dashboard stats loaded:', stats);
      
      // Update stat cards with null checks
      const totalWatermarks = document.getElementById('total-watermarks');
      const totalVerifications = document.getElementById('total-verifications');
      const storageUsed = document.getElementById('storage-used');
      const protectionScore = document.getElementById('protection-score');
      
      if (totalWatermarks) totalWatermarks.textContent = stats.total_watermarks;
      if (totalVerifications) totalVerifications.textContent = stats.total_verifications;
      if (storageUsed) storageUsed.textContent = `${stats.storage_used_mb} MB`;
      if (protectionScore) protectionScore.textContent = stats.protection_score;

      // Update recent activity
      const activityList = document.getElementById('recent-activity');
      if (activityList) {
        if (stats.recent_activity.length === 0) {
          activityList.innerHTML = `
            <div class="activity-item">
              <div class="activity-icon">📝</div>
              <div class="activity-content">
                <p>No recent activity</p>
                <div class="activity-meta">Start by watermarking your first image</div>
              </div>
            </div>
          `;
        } else {
          activityList.innerHTML = stats.recent_activity.map(item => `
            <div class="activity-item">
              <div class="activity-icon">🛡️</div>
              <div class="activity-content">
                <p>Watermarked: ${item.original_filename}</p>
                <div class="activity-meta">
                  Strength: ${item.strength} • ${formatDate(item.created_at)} • ${item.file_size_mb.toFixed(2)} MB
                </div>
              </div>
            </div>
          `).join('');
        }
      }
    } else {
      throw new Error(`Failed to load stats: ${response.status}`);
    }
  } catch (error) {
    console.error('Failed to load dashboard stats:', error);
    showNotification('Failed to load dashboard statistics', 'error');
  }
}

// Load templates
async function loadTemplates() {
  console.log('Loading templates...');
  try {
    const response = await fetch(`${API_BASE}/dashboard/templates`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    console.log('Templates response status:', response.status);

    if (response.ok) {
      const templates = await response.json();
      console.log('Templates loaded:', templates.length);
      
      const templatesGrid = document.getElementById('templates-grid');
      const bulkTemplateSelect = document.getElementById('bulk-template');
      
      if (!templatesGrid || !bulkTemplateSelect) {
        console.warn('Template elements not found in DOM');
        return;
      }
      
      if (templates.length === 0) {
        templatesGrid.innerHTML = `
          <div class="template-card">
            <p>No templates yet. Create your first template to get started!</p>
          </div>
        `;
      } else {
        templatesGrid.innerHTML = templates.map(template => `
          <div class="template-card">
            <div class="template-header">
              <h4 class="template-name">${template.name}</h4>
              ${template.is_default ? '<span class="template-badge default">Default</span>' : '<span class="template-badge">Custom</span>'}
            </div>
            <div class="template-strength">
              <span>Strength: ${template.strength}/10</span>
              <div class="strength-indicator">
                ${Array.from({length: 10}, (_, i) => 
                  `<div class="strength-dot ${i < template.strength ? 'active' : ''}"></div>`
                ).join('')}
              </div>
            </div>
            <p class="template-description">${template.description}</p>
          </div>
        `).join('');
      }

      // Populate bulk template select
      bulkTemplateSelect.innerHTML = '<option value="">Select a template...</option>' +
        templates.map(template => 
          `<option value="${template.id}">${template.name} (Strength: ${template.strength})</option>`
        ).join('');
    } else {
      throw new Error(`Failed to load templates: ${response.status}`);
    }
  } catch (error) {
    console.error('Failed to load templates:', error);
    showNotification('Failed to load templates', 'error');
  }
}

// Load analytics
async function loadAnalytics() {
  console.log('Loading analytics...');
  try {
    const response = await fetch(`${API_BASE}/dashboard/analytics`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    console.log('Analytics response status:', response.status);

    if (response.ok) {
      const analytics = await response.json();
      console.log('Analytics loaded:', analytics);
      
      // Update strength distribution with null checks
      const total = analytics.strength_distribution.light + 
                   analytics.strength_distribution.medium + 
                   analytics.strength_distribution.strong;
      
      if (total > 0) {
        const lightPercent = (analytics.strength_distribution.light / total * 100);
        const mediumPercent = (analytics.strength_distribution.medium / total * 100);
        const strongPercent = (analytics.strength_distribution.strong / total * 100);
        
        const lightBar = document.getElementById('light-bar');
        const mediumBar = document.getElementById('medium-bar');
        const strongBar = document.getElementById('strong-bar');
        const lightPercentEl = document.getElementById('light-percent');
        const mediumPercentEl = document.getElementById('medium-percent');
        const strongPercentEl = document.getElementById('strong-percent');
        
        if (lightBar) lightBar.style.width = `${lightPercent}%`;
        if (mediumBar) mediumBar.style.width = `${mediumPercent}%`;
        if (strongBar) strongBar.style.width = `${strongPercent}%`;
        
        if (lightPercentEl) lightPercentEl.textContent = `${lightPercent.toFixed(0)}%`;
        if (mediumPercentEl) mediumPercentEl.textContent = `${mediumPercent.toFixed(0)}%`;
        if (strongPercentEl) strongPercentEl.textContent = `${strongPercent.toFixed(0)}%`;
      }

      // Update key metrics with null checks
      const successRate = document.getElementById('success-rate');
      const popularTemplate = document.getElementById('popular-template');
      const protectedAssets = document.getElementById('protected-assets');
      const protectionValue = document.getElementById('protection-value');
      
      if (successRate) successRate.textContent = `${analytics.verification_success_rate}%`;
      if (popularTemplate) popularTemplate.textContent = analytics.most_used_template;
      if (protectedAssets) protectedAssets.textContent = analytics.total_protected_assets;
      if (protectionValue) protectionValue.textContent = `$${analytics.estimated_protection_value.toFixed(2)}`;

      // Draw trends chart
      drawTrendsChart(analytics.protection_trends);
    } else {
      throw new Error(`Failed to load analytics: ${response.status}`);
    }
  } catch (error) {
    console.error('Failed to load analytics:', error);
    showNotification('Failed to load analytics', 'error');
  }
}

// Draw trends chart (simple canvas implementation)
function drawTrendsChart(trends) {
  const canvas = document.getElementById('trends-canvas');
  if (!canvas) {
    console.log('Trends canvas not found, skipping chart');
    return;
  }
  
  const ctx = canvas.getContext('2d');
  const data = trends.last_7_days;
  const labels = trends.labels;
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Set up dimensions
  const padding = 40;
  const chartWidth = canvas.width - padding * 2;
  const chartHeight = canvas.height - padding * 2;
  
  // Find max value for scaling
  const maxValue = Math.max(...data);
  if (maxValue === 0) return;
  
  // Draw grid lines
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
  ctx.lineWidth = 1;
  
  for (let i = 0; i <= 4; i++) {
    const y = padding + (chartHeight / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(padding + chartWidth, y);
    ctx.stroke();
  }
  
  // Draw line chart
  ctx.strokeStyle = '#60a5fa';
  ctx.lineWidth = 2;
  ctx.beginPath();
  
  data.forEach((value, index) => {
    const x = padding + (chartWidth / (data.length - 1)) * index;
    const y = padding + chartHeight - (value / maxValue) * chartHeight;
    
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  
  ctx.stroke();
  
  // Draw points
  ctx.fillStyle = '#60a5fa';
  data.forEach((value, index) => {
    const x = padding + (chartWidth / (data.length - 1)) * index;
    const y = padding + chartHeight - (value / maxValue) * chartHeight;
    
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });
  
  // Draw labels
  ctx.fillStyle = '#9ca3af';
  ctx.font = '12px system-ui';
  ctx.textAlign = 'center';
  
  labels.forEach((label, index) => {
    const x = padding + (chartWidth / (data.length - 1)) * index;
    ctx.fillText(label, x, canvas.height - 10);
  });
}

// Setup event listeners
function setupEventListeners() {
  console.log('Setting up event listeners...');
  
  // Logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // Create template
  const createTemplateBtn = document.getElementById('create-template-btn');
  const templateForm = document.getElementById('template-form');
  
  if (createTemplateBtn) {
    createTemplateBtn.addEventListener('click', openTemplateModal);
  }
  
  if (templateForm) {
    templateForm.addEventListener('submit', createTemplate);
  }
  
  // Modal close
  const modalClose = document.querySelector('.modal-close');
  const templateModal = document.getElementById('template-modal');
  
  if (modalClose) {
    modalClose.addEventListener('click', closeTemplateModal);
  }
  
  if (templateModal) {
    templateModal.addEventListener('click', (e) => {
      if (e.target === e.currentTarget) closeTemplateModal();
    });
  }
  
  // Bulk operations
  setupBulkOperations();
  
  // Smooth scrolling for navigation
  document.querySelectorAll('nav a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
        
        // Update active nav
        document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
        link.classList.add('active');
      }
    });
  });
  
  console.log('Event listeners setup complete');
}

// Template modal functions
function openTemplateModal() {
  document.getElementById('template-modal').classList.add('active');
}

function closeTemplateModal() {
  document.getElementById('template-modal').classList.remove('active');
  document.getElementById('template-form').reset();
}

// Create template
async function createTemplate(e) {
  e.preventDefault();
  
  const formData = new FormData();
  formData.append('name', document.getElementById('template-name').value);
  formData.append('strength', document.getElementById('template-strength').value);
  formData.append('description', document.getElementById('template-description').value);
  
  try {
    const response = await fetch(`${API_BASE}/dashboard/templates`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: formData
    });
    
    if (response.ok) {
      closeTemplateModal();
      await loadTemplates();
      showNotification('Template created successfully!', 'success');
    } else {
      const error = await response.json();
      showNotification(error.detail || 'Failed to create template', 'error');
    }
  } catch (error) {
    console.error('Failed to create template:', error);
    showNotification('Failed to create template', 'error');
  }
}

// Bulk operations setup
function setupBulkOperations() {
  const dropzone = document.getElementById('bulk-dropzone');
  const input = document.getElementById('bulk-input');
  const startBtn = document.getElementById('bulk-start-btn');
  let selectedFiles = [];
  
  // Dropzone events
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
    handleFiles(e.dataTransfer.files);
  });
  
  input.addEventListener('change', (e) => {
    handleFiles(e.target.files);
  });
  
  function handleFiles(files) {
    selectedFiles = Array.from(files).slice(0, 50); // Limit to 50 files
    
    if (selectedFiles.length > 0) {
      dropzone.querySelector('p').textContent = `${selectedFiles.length} files selected`;
      startBtn.disabled = false;
    } else {
      dropzone.querySelector('p').textContent = 'Drop multiple images here';
      startBtn.disabled = true;
    }
  }
  
  // Start bulk operation
  startBtn.addEventListener('click', async () => {
    const ownerId = document.getElementById('bulk-owner-id').value.trim();
    const templateId = document.getElementById('bulk-template').value;
    
    if (!ownerId) {
      showNotification('Please enter an owner ID', 'error');
      return;
    }
    
    if (selectedFiles.length === 0) {
      showNotification('Please select files to process', 'error');
      return;
    }
    
    await startBulkOperation(selectedFiles, ownerId, templateId);
  });
}

// Start bulk operation
async function startBulkOperation(files, ownerId, templateId) {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });
  formData.append('owner_id', ownerId);
  formData.append('strength', '5'); // Default strength
  if (templateId) {
    formData.append('template_id', templateId);
  }
  
  try {
    // Update UI
    const statusDiv = document.getElementById('bulk-status');
    const progressDiv = document.getElementById('bulk-progress');
    
    statusDiv.className = 'bulk-status processing';
    statusDiv.innerHTML = `
      <div class="status-icon">⚙️</div>
      <p>Processing ${files.length} files...</p>
    `;
    progressDiv.style.display = 'block';
    
    const response = await fetch(`${API_BASE}/dashboard/bulk/watermark`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: formData
    });
    
    if (response.ok) {
      const result = await response.json();
      pollBulkOperation(result.operation_id);
    } else {
      throw new Error('Failed to start bulk operation');
    }
  } catch (error) {
    console.error('Bulk operation failed:', error);
    showNotification('Failed to start bulk operation', 'error');
  }
}

// Poll bulk operation status
async function pollBulkOperation(operationId) {
  const statusDiv = document.getElementById('bulk-status');
  const progressDiv = document.getElementById('bulk-progress');
  const resultsDiv = document.getElementById('bulk-results');
  
  const poll = async () => {
    try {
      const response = await fetch(`${API_BASE}/dashboard/bulk/${operationId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (response.ok) {
        const status = await response.json();
        
        // Update progress
        const progress = (status.processed_files + status.failed_files) / status.total_files * 100;
        document.getElementById('bulk-progress-fill').style.width = `${progress}%`;
        document.getElementById('bulk-processed').textContent = status.processed_files + status.failed_files;
        document.getElementById('bulk-total').textContent = status.total_files;
        
        if (status.status === 'completed') {
          statusDiv.className = 'bulk-status completed';
          statusDiv.innerHTML = `
            <div class="status-icon">✅</div>
            <p>Operation completed!</p>
          `;
          
          // Show results
          resultsDiv.style.display = 'block';
          resultsDiv.innerHTML = `
            <h4>Results</h4>
            <div class="result-item">
              <span>Successfully processed: ${status.processed_files}</span>
              <span class="result-status success">Success</span>
            </div>
            ${status.failed_files > 0 ? `
              <div class="result-item">
                <span>Failed: ${status.failed_files}</span>
                <span class="result-status failed">Failed</span>
              </div>
            ` : ''}
          `;
          
          // Refresh dashboard stats
          await loadDashboardStats();
          
        } else if (status.status === 'processing') {
          setTimeout(poll, 2000); // Poll every 2 seconds
        }
      }
    } catch (error) {
      console.error('Failed to poll operation status:', error);
    }
  };
  
  poll();
}

// Utility functions
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showNotification(message, type = 'info') {
  // Simple notification system
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
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
    animation: slideIn 0.3s ease;
    background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Logout function
async function logout() {
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('pngprotect_token');
    window.location.href = 'login.html';
  }
}

// Add CSS animations
if (!document.getElementById('dashboard-animations')) {
  const style = document.createElement('style');
  style.id = 'dashboard-animations';
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
    
    .dropzone.dragover {
      border-color: var(--accent-blue);
      background: rgba(96, 165, 250, 0.1);
    }
  `;
  document.head.appendChild(style);
}

// =============================
// Interactive Dashboard Features
// =============================

// Make stat cards clickable
function showStatsDetail(type) {
  let message = '';
  switch(type) {
    case 'watermarks':
      message = 'These are images you\'ve protected with invisible watermarks. Each watermark contains your ownership information.';
      break;
    case 'verifications':
      message = 'Total number of times your watermarked images have been verified for authenticity.';
      break;
    case 'storage':
      message = 'Amount of storage used by your watermark metadata and image processing data.';
      break;
    case 'score':
      message = 'Your protection score increases with more watermarked images and successful verifications. Higher scores indicate better protection coverage.';
      break;
  }
  showNotification(message, 'info');
}

// Refresh activity function
async function refreshActivity() {
  const refreshBtn = document.getElementById('refresh-activity');
  if (refreshBtn) {
    refreshBtn.innerHTML = '⏳ Refreshing...';
    refreshBtn.disabled = true;
  }
  
  await loadDashboardStats();
  
  if (refreshBtn) {
    refreshBtn.innerHTML = '🔄 Refresh';
    refreshBtn.disabled = false;
  }
  
  showNotification('Activity refreshed!', 'success');
}

// Add refresh button event listener
document.addEventListener('DOMContentLoaded', () => {
  const refreshBtn = document.getElementById('refresh-activity');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', refreshActivity);
  }
});

// Add hover effects to stat cards
document.addEventListener('DOMContentLoaded', () => {
  const statCards = document.querySelectorAll('.stat-card');
  statCards.forEach(card => {
    card.style.cursor = 'pointer';
    card.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
    
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-2px)';
      card.style.boxShadow = '0 8px 25px rgba(96, 165, 250, 0.15)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
      card.style.boxShadow = '';
    });
  });
});

// Add real-time updates (every 30 seconds)
let updateInterval;

function startRealTimeUpdates() {
  updateInterval = setInterval(async () => {
    try {
      await loadDashboardStats();
      console.log('Dashboard auto-updated');
    } catch (error) {
      console.error('Auto-update failed:', error);
    }
  }, 30000); // Update every 30 seconds
}

function stopRealTimeUpdates() {
  if (updateInterval) {
    clearInterval(updateInterval);
  }
}

// Start real-time updates when dashboard loads
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(startRealTimeUpdates, 5000); // Start after 5 seconds
});

// Stop updates when leaving the page
window.addEventListener('beforeunload', stopRealTimeUpdates);