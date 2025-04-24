document.addEventListener("trix-file-accept", function (event) {
  event.preventDefault(); // This disables all file/image uploads
});

function previewLogo(event) {
  const fileInput = event.target;
  const file = fileInput.files[0];
  const preview = document.getElementById("logo-preview");
  const imageContainer = document.getElementById("logo-container");
  const removeBtn = document.getElementById("remove-logo");

  if (file && file.type.startsWith("image/")) {
    const reader = new FileReader();

    reader.onload = function (e) {
      imageContainer.style.display = "block";
      preview.src = e.target.result;
      preview.style.display = "block";
      removeBtn.style.display = "inline-block";
    };

    reader.readAsDataURL(file);
  } else {
    imageContainer.style.display = "none";
    preview.src = "#";
    preview.style.display = "none";
    removeBtn.style.display = "none";
  }
}

function removeLogo() {
  const fileInput = document.getElementById("logo-upload");
  const preview = document.getElementById("logo-preview");
  const removeBtn = document.getElementById("remove-logo");

  fileInput.value = ""; // Clear the input
  preview.src = "#";
  preview.style.display = "none";
  removeBtn.style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
  const logoInput = document.getElementById("logo-upload");
  if (logoInput) {
    logoInput.addEventListener("change", previewLogo);
  }
});
