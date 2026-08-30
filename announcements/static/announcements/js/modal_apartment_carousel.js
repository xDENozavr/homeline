function initApartmentCarousel(images) {
  let currentIndex = 0;

  const mainImage = document.querySelector(".main-image .img_list li:nth-child(2) img");
  const pageIndicator = document.querySelector(".page");
  const thumbnails = document.querySelectorAll(".sec_but");

  if (!mainImage || !pageIndicator || thumbnails.length === 0) {
    console.warn("Carousel: elements not found");
    return;
  }

  document.querySelector(".img_list li:first-child button").addEventListener("click", () => {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    updateMainImage();
  });

  document.querySelector(".img_list li:last-child button").addEventListener("click", () => {
    currentIndex = (currentIndex + 1) % images.length;
    updateMainImage();
  });

  thumbnails.forEach((thumb, index) => {
    thumb.addEventListener("click", () => {
      currentIndex = index;
      updateMainImage();
    });
  });

  function updateMainImage() {
    mainImage.src = images[currentIndex];
    pageIndicator.textContent = `${currentIndex + 1} - ${images.length}`;
  }

  updateMainImage();
}