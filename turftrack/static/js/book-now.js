document.addEventListener("DOMContentLoaded", function () {
  const slotButtons = document.querySelectorAll(".slot .add-btn");
  const proceedBtn = document.getElementById("proceed-btn");

  const hiddenDate = document.getElementById("final-booking-date");
  const hiddenSlots = document.getElementById("final-selected-slot");
  const hiddenAmount = document.getElementById("final-selected-amount");
  const totalAmountField = document.getElementById("total_amount");

  let selectedSlots = [];
  let totalAmount = 0;

  slotButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const slotId = parseInt(btn.dataset.slotId);
      const price = parseFloat(btn.closest(".slot").querySelector("span:nth-child(2)").textContent.replace("₹", ""));

      if (!selectedSlots.includes(slotId)) {
        selectedSlots.push(slotId);
        totalAmount += price;
        btn.textContent = "×";
        btn.style.backgroundColor = "#dc3545"; // red
      } else {
        selectedSlots = selectedSlots.filter(id => id !== slotId);
        totalAmount -= price;
        btn.textContent = "+";
        btn.style.backgroundColor = "#28a745"; // green
      }

      totalAmountField.value = totalAmount.toFixed(2);
    });
  });

  proceedBtn.addEventListener("click", function (e) {
    if (selectedSlots.length === 0) {
      e.preventDefault();
      alert("Please select at least one slot.");
      return;
    }

    const activeDate = document.querySelector(".date-item.active");
    if (!activeDate) {
      e.preventDefault();
      alert("Please select a date.");
      return;
    }

    // Fill hidden inputs before submitting
    hiddenDate.value = activeDate.dataset.date;
    hiddenSlots.value = selectedSlots.join(",");
    hiddenAmount.value = totalAmount.toFixed(2);
  });
});
