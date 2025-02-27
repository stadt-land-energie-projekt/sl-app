document.addEventListener("DOMContentLoaded", function () {
    const toggleButtons = document.querySelectorAll(".btn-transparent");

    toggleButtons.forEach(button => {
        button.addEventListener("click", function () {
            const imageContainer = this.closest(".text").querySelector(".hidden-image-container");
            if (imageContainer) {
                imageContainer.classList.toggle("active");
            }
        });
    });
});
