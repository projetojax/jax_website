document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("nova-aula-form");

  form.addEventListener("submit", function (e) {
    const video = document.getElementById("nova-aula-video");
    if (video.files[0] && video.files[0].type !== "video/mp4") {
      alert("Por favor, envie um vídeo no formato MP4.");
      e.preventDefault();
    }
  });
});
