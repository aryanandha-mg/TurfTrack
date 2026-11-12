// Add interactivity for Edit and Delete buttons
document.querySelectorAll('.edit-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    alert('Redirect to Edit Turf page (frontend simulation)');
  });
});

document.querySelectorAll('.delete-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (confirm('Are you sure you want to delete this turf?')) {
      btn.closest('.turf-card').remove();
      alert('Turf deleted (frontend simulation)');
    }
  });
});
