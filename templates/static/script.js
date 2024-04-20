// **1. Fetch Supermarkets**
fetch('/supermarkets/supermarkets.json')  // Adjust path if needed
  .then(response => response.json())
  .then(supermarkets => {
    // **2. Populate Dropdown**
    const selectElement = document.getElementById('supermarket-select'); // Assuming your <select> has this ID

    supermarkets.forEach(supermarket => {
      const option = document.createElement('option');
      option.value = supermarket.id; 
      option.text = supermarket.name;
      selectElement.appendChild(option);
    });
  })
  .catch(error => console.error('Error fetching supermarkets:', error));

// **3. Submit Form Data**
const orderForm = document.querySelector('form'); // Assuming your <form> has an ID or other selector

orderForm.addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent default form submission

  const selectedSupermarketId = document.getElementById('supermarket-select').value;
  const orderDate = document.getElementById('order_date').value;

  // You might have more form fields to gather here

  // Package data for sending
  const orderData = {
    supermarket_id: selectedSupermarketId,
    order_date: orderDate
    // ... add other order details 
  };

  // Send to backend API
  fetch('/record-delivery', { // Adjust your backend endpoint
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  })
  .then(response => {
    if (response.ok) { 
        return response.json(); // Parse JSON response if needed
    } else {
        throw new Error('Network error occurred'); 
    }})
    .then(() => {
    console.log('Delivery recorded successfully!');
    // Display success message, etc.
    })
    .catch(error => {
    console.error('Error submitting order:', error);
    // Display a user-friendly error message (alert, message box, etc.)
    });
});
