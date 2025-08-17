const form = document.getElementById('userAgreementForm');

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const data = Object.fromEntries(formData);

  fetch('http://localhost:3000/append', {
    method: 'POST',
	mode: 'cors',
	body: JSON.stringify(data),
	headers: {
      'Content-Type': 'application/json'
    }})
  .then(response => response.text())
  .then(message => {
    console.log(message); // Log the success message
  })
  .catch(error => {
    // Handle errors
	console.error('Error:', error);
  });
});