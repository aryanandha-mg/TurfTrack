// Frontend simulation: Add new review to list
const form = document.getElementById('reviewForm');
const reviewsList = document.querySelector('.reviews-list');

form.addEventListener('submit', function(e) {
  e.preventDefault();

  const turfName = document.getElementById('turfName').value;
  const rating = document.getElementById('rating').value;
  const comment = document.getElementById('comment').value;

  // Create new review card
  const card = document.createElement('div');
  card.classList.add('review-card');
  card.innerHTML = `
    <h3>${turfName}</h3>
    <p><strong>Rating:</strong> ${rating}/5</p>
    <p><strong>Comment:</strong> ${comment}</p>
    <p><em>by You</em></p>
  `;

  reviewsList.appendChild(card);

  // Reset form
  form.reset();
});
document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("reviewForm");

  form.addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent the default form submit action

    // Optional: validate data before submitting
    const turfName = document.getElementById("turfName").value.trim();
    const rating = document.getElementById("rating").value.trim();
    const comment = document.getElementById("comment").value.trim();

    if (!turfName || !rating || !comment) {
      alert("Please fill out all fields before submitting.");
      return;
    }

    // Show alert box
    alert("Review submitted successfully!");

    // Now submit the form to Django
    form.submit();
  });
});
