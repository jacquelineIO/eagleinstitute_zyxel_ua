// Script for Python server integration
// This replaces the original script.js when using Python backend

// Auto-detect environment based on hostname
const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1' ||
                window.location.hostname === '';  // file:// protocol

const PORT =  8080;

const PYTHON_SERVER_URL = isLocal
  ? `http://localhost:${PORT}/append`
  : `http://192.168.50.19:${PORT}/append`;

console.log('Portal running in', isLocal ? 'LOCAL' : 'PRODUCTION', 'mode');
console.log('Using server:', PYTHON_SERVER_URL);

// Health check on page load
window.addEventListener('load', function() {
  const healthUrl = PYTHON_SERVER_URL.replace('/append', '/health');
  fetch(healthUrl)
    .then(response => {
      if (response.ok) {
        console.log('✅ Python server is reachable at:', PYTHON_SERVER_URL);
      } else {
        throw new Error('Server responded with: ' + response.status);
      }
    })
    .catch(error => {
      console.error('❌ Cannot reach Python server at:', PYTHON_SERVER_URL);
      console.error('Error:', error.message);
      if (isLocal) {
        alert(`Warning: Email collection server not running.\nPlease start the Python server on port ${PORT}.\n\nRun: python3 server/captive_portal_server.py`);
      }
    });
});

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('userAgreementForm');
  const submitButton = document.getElementById('submitButton');
  
  // Debug button functionality
  const btn = document.getElementById("debugButton");
  const out = document.getElementById("debugOutput");

  if (btn) {
    btn.addEventListener("click", () => {
      out.textContent = "Testing connection to API...";
      console.log(`[DEBUG] Testing API connection to port ${PORT}...`);
      
      // Use the same URL logic as the main form
      const healthUrl = PYTHON_SERVER_URL.replace('/append', '/health');
      console.log('[DEBUG] Testing URL:', healthUrl);

      fetch(healthUrl)
        .then(resp => {
          console.log('[DEBUG] Response status:', resp.status);
          return resp.text();
        })
        .then(txt => {
          out.textContent = "✅ Success:\n" + txt;
          console.log('[DEBUG] API test successful:', txt);
        })
        .catch(err => {
          out.textContent = "❌ Error:\n" + err;
          console.error("[DEBUG] API test failed:", err);
        });
    });
  }

  if (form && submitButton) {
    // Remove the onclick from the button to prevent the original sendSubmit
    submitButton.removeAttribute('onclick');
    
    // Handle form submission
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      event.stopPropagation();
      console.log('[DEBUG] Form submit triggered');

      // Get email value
      const emailInput = document.getElementById('field1');
      console.log('[DEBUG] Email input element:', emailInput);
      console.log('[DEBUG] Email value:', emailInput ? emailInput.value : 'null');
      
      if (!emailInput || !emailInput.value) {
        console.log('[DEBUG] No email provided');
        alert('Please enter your email address');
        return false;
      }

      // Validate email format
      const emailRegex = /^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/i;
      if (!emailRegex.test(emailInput.value)) {
        console.log('[DEBUG] Invalid email format:', emailInput.value);
        alert('Please enter a valid email address');
        return false;
      }

      const data = { field1: emailInput.value };
      console.log('[DEBUG] Sending data to server:', data);
      console.log('[DEBUG] Server URL:', PYTHON_SERVER_URL);

      // Show loading state
      submitButton.disabled = true;
      submitButton.value = 'Submitting...';

      // Send to Python server
      console.log('[DEBUG] Starting fetch request...');
      fetch(PYTHON_SERVER_URL, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response => {
        console.log('[DEBUG] Server response received:', response.status, response.statusText);
        if (!response.ok) {
          throw new Error('Server responded with ' + response.status);
        }
        return response.text();
      })
      .then(message => {
        console.log('[DEBUG] Success message from server:', message);
        
        if (isLocal) {
          // Local testing - just show success and reset
          alert('Email registered successfully! (Local test mode)');
          form.reset();
          submitButton.disabled = false;
          submitButton.value = 'Accept and Connect';
        } else {
          // Production - submit to Zyxel CGI for WiFi authentication
          console.log('Submitting to Zyxel portal for authentication...');
          form.action = '/agree.cgi';
          form.method = 'POST';
          
          // Remove our event listener to allow normal submission
          const newForm = form.cloneNode(true);
          form.parentNode.replaceChild(newForm, form);
          newForm.submit();
        }
      })
      .catch(error => {
        console.error('[DEBUG] Fetch error:', error);
        console.error('[DEBUG] Error stack:', error.stack);
        alert(`Failed to register email. Please check the Python server is running on port ${PORT}.\n\nError: ${error.message}`);
        
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.value = 'Accept and Connect';
      });

      return false;
    });
  }
});