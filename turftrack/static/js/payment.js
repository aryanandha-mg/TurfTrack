document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".payment-form");
  const amount = document.querySelector(".pay-btn").innerText.match(/\d+/)[0];

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const cardNumber = document.getElementById("card-number").value.trim();
    const expiry = document.getElementById("expiry").value.trim();
    const cvv = document.getElementById("cvv").value.trim();

    if (!name || !cardNumber || !expiry || !cvv) {
      alert("Please fill in all fields.");
      return;
    }

    if (cardNumber.length !== 16 || isNaN(cardNumber)) {
      alert("Card number must be 16 digits.");
      return;
    }

    if (!/^\d{2}\/\d{2}$/.test(expiry)) {
      alert("Expiry date must be in MM/YY format.");
      return;
    }

    if (cvv.length !== 3 || isNaN(cvv)) {
      alert("CVV must be 3 digits.");
      return;
    }

    alert(`Payment of ₹${amount} Successful! 🎉 Your booking is confirmed.`);
    window.location.href = "/booking-confirmation";
  });
});
