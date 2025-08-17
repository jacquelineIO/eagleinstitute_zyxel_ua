// Configuration for captive portal
// This file should be included in the HTML pages

// Server configuration
const PORTAL_CONFIG = {
    // For Zyxel deployment - point to Windows server IP
    serverUrl: 'http://192.168.50.19:8080',
    
    // For local testing
    // serverUrl: 'http://localhost:8080',
    
    // Endpoint for email submission
    endpoint: '/append'
};

// Function to submit email to server
function submitEmailToPortal(email) {
    const data = { field1: email };
    
    return fetch(PORTAL_CONFIG.serverUrl + PORTAL_CONFIG.endpoint, {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(message => {
        console.log('Success:', message);
        return message;
    })
    .catch(error => {
        console.error('Error:', error);
        throw error;
    });
}