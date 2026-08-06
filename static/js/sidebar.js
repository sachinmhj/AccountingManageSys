document.addEventListener("DOMContentLoaded", () => {

    const toggles = document.querySelectorAll(".submenu-toggle");

    toggles.forEach(toggle => {

        toggle.addEventListener("click", () => {

            toggle.parentElement.classList.toggle("open");

        });

    });

});