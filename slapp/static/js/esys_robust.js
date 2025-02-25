document.addEventListener("DOMContentLoaded", function() {
    const dropdownToggle = document.querySelector("#info-dropdown");
    const dropdownMenu = document.querySelector(".dropdown");

    dropdownToggle.addEventListener("click", function(event) {
        dropdownMenu.classList.toggle("show");
        event.stopPropagation();
    });

    document.addEventListener("click", function(event) {
        if (!dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove("show");
        }
    });
});
