// Script for Python server integration
// This replaces the original script.js when using Python backend

// Configuration - change this based on your deployment
const PYTHON_SERVER_URL = 'http://192.168.50.19:8080/append';
// For local testing, use: 'http://localhost:8080/append'

const form = document.getElementById('userAgreementForm');

if (form) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Show loading state
    const submitButton = document.getElementById('submitButton');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.value = 'Connecting...';
    }

    fetch(PYTHON_SERVER_URL, {
      method: 'POST',
      mode: 'cors',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(message => {
      console.log(message); // Log the success message
      
      // Submit the form to Zyxel for authentication
      // This allows the captive portal to continue its flow
      if (typeof sendSubmit === 'function') {
        // Call the original sendSubmit if it exists
        document.form.submit();
      } else {
        // Direct submit as fallback
        document.form.submit();
      }
    })
    .catch(error => {
      // Handle errors
      console.error('Error:', error);
      alert('Failed to register email. Please try again.');
      
      // Re-enable submit button
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.value = 'Accept and Connect';
      }
    });
  });
}