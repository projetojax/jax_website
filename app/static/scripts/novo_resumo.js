document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("image");

    imageInput.addEventListener("change", function () {
        if (this.files && this.files[0]) {
            alert("Imagem selecionada: " + this.files[0].name);
        }
    });
});
