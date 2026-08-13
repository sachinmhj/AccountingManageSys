document.addEventListener("DOMContentLoaded", function () {
    // Select-all checkbox functionality
    const nameCheckbox = document.getElementById("name-checkbox");
    const itemCheckboxes = document.querySelectorAll(".row-checkbox:not(#name-checkbox)");

    if (nameCheckbox) {
        nameCheckbox.addEventListener("change", function () {
            itemCheckboxes.forEach(function (checkbox) {
                checkbox.checked = nameCheckbox.checked;
            });
        });
    }
});

/**
 * Toggle Action Menu Dropdown (3 Dots)
 */
function toggleMenu(event, button) {
    event.stopPropagation();
    
    const menu = button.nextElementSibling;
    
    // Close all other open dropdown menus first
    document.querySelectorAll(".dropdown-menu").forEach(function (item) {
        if (item !== menu) {
            item.classList.remove("show");
        }
    });

    // Toggle current dropdown menu visibility
    menu.classList.toggle("show");
}

/**
 * Close all dropdown menus on click outside
 */
document.addEventListener("click", function (event) {
    if (!event.target.closest(".action-menu")) {
        document.querySelectorAll(".dropdown-menu").forEach(function (menu) {
            menu.classList.remove("show");
        });
    }
});


function openCategoryModal() {
    const modal = document.getElementById("createCategoryModalOverlay");
    if (modal) {
        modal.style.display = "flex";
    }
}

function openEditCategoryModal(id, name, parent, description) {

    document.querySelectorAll(".dropdown-menu").forEach(m => m.classList.remove("show"));

    const idInput = document.getElementById("editCategoryId");
    const nameInput = document.getElementById("editCategoryName");
    const parentSelect = document.getElementById("editCategoryParent");
    const descInput = document.getElementById("editCategoryDescription");

    if (idInput) idInput.value = id || "";
    if (nameInput) nameInput.value = name || "";
    if (parentSelect) parentSelect.value = parent || "";
    if (descInput) descInput.value = description || "";

    // Show Edit Modal
    const modal = document.getElementById("editCategoryModalOverlay");
    if (modal) {
        modal.style.display = "flex";
    }
}

function closeCategoryModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    }
}