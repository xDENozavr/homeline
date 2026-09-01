document.addEventListener("DOMContentLoaded", function () {
  const modalContainer = document.getElementById("modal-container");
  const modalContent = document.getElementById("modal-content");

  const mainImageButton = document.getElementById("open-modal");

  if (mainImageButton) {
    mainImageButton.addEventListener("click", function () {
      const announcementId = mainImageButton.dataset.anId;

      fetch(`/announcement/${announcementId}/modal_apartment_photo/`)
        .then(response => response.text())
        .then(data => {
          modalContent.innerHTML = data;
          modalContainer.classList.remove("hidden");

          setupModalButtons();

          // initShowButtons is defined globally in phone_and_link.js
          // — it needs to be re-run here since buttons inserted via
          // innerHTML don't get their click listeners automatically.
          if (typeof initShowButtons === "function") {
            initShowButtons(modalContent);
          }

          const mainImg = modalContent.querySelector(".announcement_main_img");
          const thumbImgs = modalContent.querySelectorAll(".sec_but img");
          if (mainImg && typeof initApartmentCarousel === "function") {
            const images = [mainImg.src, ...Array.from(thumbImgs).map(img => img.src)];
            initApartmentCarousel(images);
          }
        })
        .catch(error => console.error("Error loading modal:", error));
    });
  }

  if (modalContainer) {
    modalContainer.addEventListener("click", function (e) {
      if (e.target === modalContainer) {
        modalContainer.classList.add("hidden");
        modalContent.innerHTML = "";
      }
    });
  }

  function setupModalButtons() {
    const closeButton = modalContent.querySelector(".close-button");
    if (closeButton) {
      closeButton.addEventListener("click", function () {
        modalContainer.classList.add("hidden");
        modalContent.innerHTML = "";
      });
    } else {
      console.log("Close button not found inside modalContent");
    }

    const backButton = modalContent.querySelector(".back-button");
    if (backButton) {
      backButton.addEventListener("click", function () {
        window.history.back();
      });
    } else {
      console.log("Back button not found inside modalContent");
    }
  }
});