// Tab switching
const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    // remove active from all
    tabButtons.forEach(b => b.classList.remove("active"));
    tabContents.forEach(c => c.classList.remove("active"));

    // add active to current
    btn.classList.add("active");
    document.getElementById(btn.dataset.target).classList.add("active");
  });
});

// Example action button click (later link to Django views)
document.querySelectorAll(".action-btn").forEach(button => {
  button.addEventListener("click", () => {
    alert("Redirect to form page (Django integration)");
  });
});