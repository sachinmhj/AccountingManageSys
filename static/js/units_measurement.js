document.addEventListener("DOMContentLoaded", function () {
    // ----------------------------------------------------
    // 1. GLOBAL SEARCH FUNCTIONALITY
    // ----------------------------------------------------
    const globalSearch = document.getElementById("globalSearchInput");

    if (globalSearch) {
        globalSearch.addEventListener("input", filterUnitsTable);
        globalSearch.addEventListener("keyup", filterUnitsTable);
    }

    // ----------------------------------------------------
    // 2. SELECT ALL CHECKBOX FUNCTIONALITY
    // ----------------------------------------------------
    const selectAllCheckbox = document.getElementById("selectAllCheckbox");

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener("change", function () {
            const rowCheckboxes = document.querySelectorAll("#unitsTable tbody .unit-checkbox");
            rowCheckboxes.forEach(checkbox => {
                // Only select checkboxes of visible rows (respects active search filter)
                const parentRow = checkbox.closest("tr");
                if (parentRow && parentRow.style.display !== "none") {
                    checkbox.checked = selectAllCheckbox.checked;
                }
            });
        });
    }

    // Keep "Select All" state in sync when individual row checkboxes are manually clicked
    document.addEventListener("change", function (e) {
        if (e.target && e.target.classList.contains("unit-checkbox")) {
            const visibleCheckboxes = Array.from(document.querySelectorAll("#unitsTable tbody .unit-checkbox"))
                .filter(cb => cb.closest("tr").style.display !== "none");
            
            const allChecked = visibleCheckboxes.length > 0 && visibleCheckboxes.every(cb => cb.checked);
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = allChecked;
            }
        }
    });

    // ----------------------------------------------------
    // 3. "ADD NEW" BUTTON TRIGGER
    // ----------------------------------------------------
    // Targets common button selectors used in erp_list_header.html
    const addNewBtn = document.querySelector(".btn-add-unit, .btn-create, [data-action='add-new']");
    if (addNewBtn) {
        addNewBtn.addEventListener("click", function (e) {
            e.preventDefault();
            openCreateUnitModal();
        });
    }

    // Update row counters on initial load
    updateCounts();
});

// ----------------------------------------------------
// HELPER FUNCTIONS
// ----------------------------------------------------

function filterUnitsTable() {
    const searchInput = document.getElementById("globalSearchInput");
    if (!searchInput) return;

    const query = searchInput.value.toLowerCase().trim();
    const rows = document.querySelectorAll("#unitsTable tbody tr.unit-row");
    let visibleCounter = 0;

    rows.forEach(row => {
        const nameCell = row.querySelector(".unit-name");
        const shortNameCell = row.querySelector(".unit-short-name");

        const nameText = nameCell ? nameCell.textContent.toLowerCase() : "";
        const shortNameText = shortNameCell ? shortNameCell.textContent.toLowerCase() : "";

        if (nameText.includes(query) || shortNameText.includes(query)) {
            row.style.display = "";
            visibleCounter++;
        } else {
            row.style.display = "none";
        }
    });

    const visibleCountElem = document.getElementById("visibleCount");
    if (visibleCountElem) {
        visibleCountElem.textContent = visibleCounter;
    }

    // Reset Select All state when search query changes
    const selectAllCheckbox = document.getElementById("selectAllCheckbox");
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
    }
}

function updateCounts() {
    const allRows = document.querySelectorAll("#unitsTable tbody tr.unit-row");
    const visibleRows = Array.from(allRows).filter(r => r.style.display !== "none");

    const visibleCountElem = document.getElementById("visibleCount");
    const totalCountElem = document.getElementById("totalCount");

    if (visibleCountElem) visibleCountElem.textContent = visibleRows.length;
    if (totalCountElem) totalCountElem.textContent = allRows.length;
}

// Action dropdown logic
function toggleMenu(event, element) {
    event.stopPropagation();
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        if (menu !== element.nextElementSibling) {
            menu.classList.remove('show');
        }
    });
    const currentMenu = element.nextElementSibling;
    if (currentMenu) {
        currentMenu.classList.toggle('show');
    }
}

document.addEventListener('click', function () {
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.classList.remove('show');
    });
});

// Modal Handlers
function openCreateUnitModal() {
    const createModal = document.getElementById("createUnitModalOverlay");
    if (createModal) {
        createModal.style.display = "flex";
    }
}

function closeUnitModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    }
}

function openEditUnitModal(id, name, shortName, description, acceptsFraction) {
    document.getElementById('editUnitId').value = id;
    document.getElementById('editUnitName').value = name;
    document.getElementById('editUnitShortName').value = shortName;
    document.getElementById('editUnitDescription').value = description || '';
    document.getElementById('editUnitAcceptsFraction').checked = (acceptsFraction === 'true');
    document.getElementById('editUnitModalOverlay').style.display = 'flex';
}