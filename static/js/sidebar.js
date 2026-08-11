document.addEventListener("DOMContentLoaded", () => {

    const toggles = document.querySelectorAll(".submenu-toggle");

    toggles.forEach(toggle => {

        toggle.addEventListener("click", () => {

            toggle.parentElement.classList.toggle("open");

        });

    });

});

function toggleSidebar() {

    const sidebar = document.querySelector(".sidebar");

    if (sidebar) {
        sidebar.classList.toggle("open");
    }

}