document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("menuToggle");
    const navbar = document.getElementById("navbar");

    toggleBtn.addEventListener("click", function () {
        navbar.classList.toggle("hidden");
    });
});
