document.addEventListener("DOMContentLoaded", () => {
  const slides = document.querySelectorAll('.journey-slide');
  const wrapper = document.querySelector('.journey-wrapper');
  let currentSlide = 0;

  function updateSlides() {
    wrapper.style.transform = `translateX(-${currentSlide * 100}%)`;
    slides.forEach((slide, index) => {
      slide.classList.toggle('active', index === currentSlide);
    });
  }

  document.getElementById('nextBtn').addEventListener('click', () => {
    if (currentSlide < slides.length - 1) {
      currentSlide++;
      updateSlides();
    }
  });

  document.getElementById('prevBtn').addEventListener('click', () => {
    if (currentSlide > 0) {
      currentSlide--;
      updateSlides();
    }
  });

  updateSlides(); // inicializa
});
