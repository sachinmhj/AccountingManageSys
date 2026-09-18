// Immediately run to prevent flash of expanded sidebar on desktop if saved state is 'closed'
(function () {
    if (window.innerWidth > 767 && localStorage.getItem("sidebarState") === "closed") {
        document.documentElement.classList.add("sidebar-closed-init");
    }
})();

document.addEventListener("DOMContentLoaded", () => {
    // Remove temporary initialization class once DOM is ready
    document.documentElement.classList.remove("sidebar-closed-init");

    const layout = document.querySelector(".app-layout");
    if (window.innerWidth > 767) {
        if (localStorage.getItem("sidebarState") === "closed" && layout) {
            layout.classList.add("sidebar-closed");
        }
    }

    // Submenu accordion toggles
    const toggles = document.querySelectorAll(".submenu-toggle");
    toggles.forEach(toggle => {
        toggle.addEventListener("click", () => {
            toggle.parentElement.classList.toggle("open");
        });
    });
});

function toggleSidebar() {
    const layout = document.querySelector(".app-layout");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    if (window.innerWidth <= 767) {
        // Mobile view: slide drawer in/out
        if (sidebar) {
            sidebar.classList.toggle("open");
            if (overlay) {
                overlay.classList.toggle("active", sidebar.classList.contains("open"));
            }
        }
    } else {
        // Desktop view: collapse grid column
        if (layout) {
            layout.classList.toggle("sidebar-closed");
            const isClosed = layout.classList.contains("sidebar-closed");
            localStorage.setItem("sidebarState", isClosed ? "closed" : "open");
        }
    }
}