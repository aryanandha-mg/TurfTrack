document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("image");
  const imagePreview = document.getElementById("imagePreview");
  const form = document.getElementById("addTurfForm");

  // Preview selected image
  imageInput.addEventListener("change", function () {
    const file = this.files[0];

    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Turf Preview">`;
      };
      reader.readAsDataURL(file);
    } else {
      imagePreview.innerHTML = "<span>No image selected</span>";
    }
  });

  // Simulate form submission
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    alert("Turf details saved successfully (Frontend only)!");
    form.reset();
    imagePreview.innerHTML = "<span>No image selected</span>";
  });
});
