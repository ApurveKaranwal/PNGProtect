// Authentication JavaScript
// API_BASE is already declared globally in script.js

document.addEventListener('DOMContentLoaded', () => {
  console.log('Auth page loaded');
  
  // Check if user is already logged in
  const token = localStorage.getItem('pngprotect_token');
  if (token && (window.location.pathname.includes('login.html') || window.location.pathname.includes('register.html'))) {
    console.log('User already logged in, redirecting to dashboard...');
    window.location.href = 'dashboard.html';
    return;
  }

  setupAuthForms();
  
  // Initialize particles if the function exists
  if (typeof initParticles === 'function') {
    initParticles();
  }
});

function setupAuthForms() {
  console.log('Setting up auth forms...');
  
  // Login form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    console.log('Login form found');
    loginForm.addEventListener('submit', handleLogin);
  }

  // Demo login button - Enhanced implementation
  const demoBtn = document.getElementById('demo-login');
  if (demoBtn) {
    console.log('Demo button found, attaching event listener');
    demoBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      console.log('Demo button clicked');
      
      // Show loading state immediately
      const originalText = demoBtn.innerHTML;
      demoBtn.innerHTML = '<span>⏳</span> Signing in...';
      demoBtn.disabled = true;
      
      // Fill in demo credentials visually
      const emailField = document.getElementById('email');
      const passwordField = document.getElementById('password');
      
      if (emailField && passwordField) {
        emailField.value = 'demo@pngprotect.com';
        passwordField.value = 'demo123';
        console.log('Demo credentials filled');
        
        // Add visual feedback
        emailField.style.borderColor = '#22c55e';
        passwordField.style.borderColor = '#22c55e';
        
        // Small delay for visual feedback
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Trigger login directly
        try {
          await performLogin('demo@pngprotect.com', 'demo123');
        } catch (error) {
          console.error('Demo login failed:', error);
          // Reset button state
          demoBtn.innerHTML = originalText;
          demoBtn.disabled = false;
          // Reset field colors
          emailField.style.borderColor = '';
          passwordField.style.borderColor = '';
        }
      } else {
        console.error('Email or password field not found');
        showNotification('Form fields not found', 'error');
        // Reset button state
        demoBtn.innerHTML = originalText;
        demoBtn.disabled = false;
      }
    });
  } else {
    console.error('Demo button not found');
  }

  // Register form
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
  }
}

async function handleLogin(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  await performLogin(email, password);
}

async function performLogin(email, password) {
  console.log('Performing login for:', email);
  console.log('API_BASE value:', typeof API_BASE !== 'undefined' ? API_BASE : 'UNDEFINED');
  
  if (typeof API_BASE === 'undefined') {
    console.error('API_BASE is not defined! Make sure script.js loads before auth.js');
    showNotification('Configuration error: API_BASE not defined', 'error');
    return;
  }
  
  if (!email || !password) {
    showNotification('Please enter both email and password', 'error');
    return;
  }
  
  const submitBtn = document.querySelector('button[type="submit"]');
  
  // Show loading state
  setButtonLoading(submitBtn, true);
  
  try {
    console.log('Sending login request to:', `${API_BASE}/auth/login`);
    
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    console.log('Login response status:', response.status);
    console.log('Login response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Login error response:', errorData);
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Login successful:', data.user.full_name);
    
    // Store token
    localStorage.setItem('pngprotect_token', data.token);
    
    // Verify token was stored
    const storedToken = localStorage.getItem('pngprotect_token');
    console.log('Token stored successfully:', !!storedToken);
    
    showNotification(`Welcome back, ${data.user.full_name}! Redirecting...`, 'success');
    
    // Redirect after short delay
    setTimeout(() => {
      console.log('Redirecting to dashboard...');
      window.location.href = 'dashboard.html';
    }, 1500);
    
  } catch (error) {
    console.error('Login error:', error);
    
    let errorMessage = 'Login failed';
    if (error.message.includes('Failed to fetch')) {
      errorMessage = 'Cannot connect to server. Please check if the backend is running on port 8000.';
    } else if (error.message.includes('NetworkError')) {
      errorMessage = 'Network error. Please check your connection and try again.';
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    showNotification(errorMessage, 'error');
  } finally {
    setButtonLoading(submitBtn, false);
    
    // Reset demo button if it was used
    const demoBtn = document.getElementById('demo-login');
    if (demoBtn && demoBtn.disabled) {
      demoBtn.innerHTML = '<span>🚀</span> Use Demo Account';
      demoBtn.disabled = false;
    }
  }
}

async function handleRegister(e) {
  e.preventDefault();
  
  const fullName = document.getElementById('full-name').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const role = document.getElementById('role').value;
  const submitBtn = document.querySelector('button[type="submit"]');
  
  // Basic validation
  if (password.length < 6) {
    showNotification('Password must be at least 6 characters long', 'error');
    return;
  }
  
  // Show loading state
  setButtonLoading(submitBtn, true);
  
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        full_name: fullName,
        email,
        password,
        role
      }),
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store token and redirect
      localStorage.setItem('pngprotect_token', data.token);
      showNotification('Account created successfully! Redirecting...', 'success');
      
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 1500);
    } else {
      showNotification(data.detail || 'Registration failed', 'error');
    }
  } catch (error) {
    console.error('Registration error:', error);
    showNotification('Network error. Please try again.', 'error');
  } finally {
    setButtonLoading(submitBtn, false);
  }
}

function setButtonLoading(button, loading) {
  if (!button) return;
  
  const label = button.querySelector('.btn-label');
  const spinner = button.querySelector('.btn-spinner');
  
  if (loading) {
    button.disabled = true;
    if (label) label.style.opacity = '0.7';
    if (spinner) spinner.style.display = 'inline-block';
  } else {
    button.disabled = false;
    if (label) label.style.opacity = '1';
    if (spinner) spinner.style.display = 'none';
  }
}

function showNotification(message, type = 'info') {
  // Remove existing notifications
  const existing = document.querySelector('.notification');
  if (existing) existing.remove();
  
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOutRight 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}