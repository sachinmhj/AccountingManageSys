/* =====================================================
   PRODUCT DROPDOWN
===================================================== */

function toggleProductDropdown(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const popup = document.getElementById("productDropdownPopup");

    if (!popup) return;

    const isActive = popup.classList.contains("active");

    closeAllPopups();

    if (!isActive) {
        popup.classList.add("active");
    }
}


/* =====================================================
   PRODUCT MODAL
===================================================== */

function openProductModal(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    closeAllPopups();

    const modal = document.getElementById("productModalOverlay");

    if (modal) {
        modal.style.display = "flex";
    }
}


function closeProductModal() {
    const modal = document.getElementById("productModalOverlay");

    if (modal) {
        modal.style.display = "none";
    }
}


/* =====================================================
   PRODUCT TYPE
===================================================== */

function setProductType(type) {
    const typeValue = document.getElementById("productTypeValue");
    const goodsBtn = document.getElementById("typeGoodsBtn");
    const servicesBtn = document.getElementById("typeServicesBtn");
    const modalTypeValue =
        document.getElementById("productTypeValueModal");

    const modalGoodsBtn =
        document.getElementById("typeGoodsBtnModal");

    const modalServicesBtn =
        document.getElementById("typeServicesBtnModal");
    if (typeValue) {
        typeValue.value = type;
    }

    if (goodsBtn && servicesBtn) {

        if (type === "Goods") {
            goodsBtn.classList.add("active");
            servicesBtn.classList.remove("active");
        } else {
            servicesBtn.classList.add("active");
            goodsBtn.classList.remove("active");
        }
    }
    if (modalTypeValue) {
        modalTypeValue.value = type;
    }

    if (modalGoodsBtn && modalServicesBtn) {

        if (type === "Goods") {
            modalGoodsBtn.classList.add("active");
            modalServicesBtn.classList.remove("active");
        } else {
            modalServicesBtn.classList.add("active");
            modalGoodsBtn.classList.remove("active");
        }
    }
}


/* =====================================================
   SAVE PRODUCT
===================================================== */

function saveNewProduct() {

    const form = document.getElementById("newProductForm");

    if (form && !form.checkValidity()) {
        form.reportValidity();
        return;
    }

    alert("New Product Saved!");

    closeProductModal();
}


/* =====================================================
   CATEGORY DROPDOWN
   Works for BOTH main form and modal
===================================================== */

function toggleCategoryDropdown(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const trigger = e.currentTarget;

    if (!trigger) return;

    /*
     * Find the Category container that belongs
     * to the clicked trigger.
     */
    const container =
        trigger.closest(".category-picker-container");

    if (!container) return;

    /*
     * Find the dropdown INSIDE this container.
     */
    const popup =
        container.querySelector(".custom-dropdown-popup");

    if (!popup) return;

    const isActive =
        popup.classList.contains("active");

    closeAllPopups();

    if (!isActive) {
        popup.classList.add("active");
    }
}


function selectCategory(name, e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const item = e?.currentTarget;

    /*
     * If called from saveNewCategory()
     * without an event, use the first available
     * category container.
     */
    let container = null;

    if (item) {
        container =
            item.closest(".category-picker-container");
    }

    if (!container) {

        container =
            document.querySelector(
                ".category-picker-container"
            );
    }

    if (!container) return;


    /*
     * Find the input belonging to THIS category picker.
     */
    const searchInput =
        container.querySelector(
            'input[id^="categorySearchInput"]'
        );

    const hiddenInput =
        container.querySelector(
            'input[id^="selectedCategoryId"]'
        );

    const popup =
        container.querySelector(
            ".custom-dropdown-popup"
        );


    if (searchInput) {
        searchInput.value = name;
    }

    if (hiddenInput) {
        hiddenInput.value = name;
    }

    if (popup) {
        popup.classList.remove("active");
    }
}


/* =====================================================
   CATEGORY MODAL
===================================================== */

function openCategoryModal(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /*
     * Close dropdown popups without closing
     * the main/product modal.
     */
    closeAllPopups();

    const modal =
        document.getElementById("categoryModalOverlay");

    if (modal) {
        modal.style.display = "flex";
    }
}


function closeCategoryModal() {

    const modal =
        document.getElementById("categoryModalOverlay");

    if (modal) {
        modal.style.display = "none";
    }
}


function saveNewCategory() {

    const nameInput =
        document.getElementById("newCategoryName");

    if (!nameInput || !nameInput.value.trim()) {

        alert("Please enter a category name.");

        return;
    }

    const categoryName =
        nameInput.value.trim();


    /*
     * Add new category to MAIN category dropdown.
     */
    const list =
        document.getElementById("categoryOptionsList");

    if (list) {

        const item =
            document.createElement("div");

        item.className =
            "dropdown-option-item";

        item.textContent =
            categoryName;

        item.onclick =
            function (e) {
                selectCategory(categoryName, e);
            };

        list.appendChild(item);
    }


    /*
     * Also add to MODAL category dropdown.
     */
    const modalList =
        document.getElementById("categoryOptionsListModal");

    if (modalList) {

        const modalItem =
            document.createElement("div");

        modalItem.className =
            "dropdown-option-item";

        modalItem.textContent =
            categoryName;

        modalItem.onclick =
            function (e) {
                selectCategory(categoryName, e);
            };

        modalList.appendChild(modalItem);
    }


    /*
     * Add to parent category select if present.
     */
    const parentSelect =
        document.getElementById("underCategorySelect");

    if (parentSelect) {

        const option =
            document.createElement("option");

        option.value =
            categoryName;

        option.textContent =
            categoryName;

        parentSelect.appendChild(option);
    }


    /*
     * Clear input.
     */
    nameInput.value = "";


    /*
     * Close category modal.
     */
    closeCategoryModal();
}


/* =====================================================
   PRIMARY UNIT DROPDOWN
   Works for BOTH main form and modal
===================================================== */

function toggleUnitDropdown(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const trigger =
        e.currentTarget;

    if (!trigger) return;

    /*
     * Find the Unit container belonging
     * to the clicked trigger.
     */
    const container =
        trigger.closest(".unit-picker-container");

    if (!container) return;


    /*
     * Find dropdown inside this container.
     */
    const popup =
        container.querySelector(".unit-dropdown-card") ||
        container.querySelector(".unit-popup");

    if (!popup) return;


    const isActive =
        popup.classList.contains("active");

    closeAllPopups();

    if (!isActive) {
        popup.classList.add("active");
    }
}


function selectUnit(unitName, e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const item =
        e?.currentTarget;


    /*
     * Find the Unit container belonging
     * to the clicked option.
     */
    let container = null;

    if (item) {
        container =
            item.closest(".unit-picker-container");
    }


    /*
     * If called from saveNewUnit()
     * without event, use the first Unit picker.
     */
    if (!container) {

        container =
            document.querySelector(
                ".unit-picker-container"
            );
    }

    if (!container) return;


    /*
     * Find inputs inside THIS unit picker.
     */
    const hiddenInput =
        container.querySelector(
            'input[id^="selectedUnitId"]'
        );

    const searchInput =
        container.querySelector(
            'input[id^="unitSearchInput"]'
        );

    const popup =
        container.querySelector(".unit-dropdown-card") ||
        container.querySelector(".unit-popup");


    if (hiddenInput) {
        hiddenInput.value = unitName;
    }

    if (searchInput) {
        searchInput.value = unitName;
    }

    if (popup) {
        popup.classList.remove("active");
    }
}


/* =====================================================
   UNIT MODAL
===================================================== */

function openUnitModal(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /*
     * Close dropdowns without closing parent modal.
     */
    closeAllPopups();

    const modal =
        document.getElementById("unitModalOverlay");

    if (modal) {
        modal.style.display = "flex";
    }
}


function closeUnitModal() {

    const modal =
        document.getElementById("unitModalOverlay");

    if (modal) {
        modal.style.display = "none";
    }
}


function saveNewUnit() {

    const nameInput =
        document.getElementById("newUnitName");

    if (!nameInput || !nameInput.value.trim()) {

        alert("Please enter a unit name.");

        return;
    }

    const unitName =
        nameInput.value.trim();


    /*
     * Add to MAIN unit dropdown.
     */
    const list =
        document.getElementById("unitOptionsList");

    if (list) {

        const item =
            document.createElement("div");

        item.className =
            "dropdown-option-item";

        item.textContent =
            unitName;

        item.onclick =
            function (e) {
                selectUnit(unitName, e);
            };

        list.appendChild(item);
    }


    /*
     * Add to MODAL unit dropdown.
     */
    const modalList =
        document.getElementById("unitOptionsListModal");

    if (modalList) {

        const modalItem =
            document.createElement("div");

        modalItem.className =
            "dropdown-option-item";

        modalItem.textContent =
            unitName;

        modalItem.onclick =
            function (e) {
                selectUnit(unitName, e);
            };

        modalList.appendChild(modalItem);
    }


    /*
     * Clear unit name.
     */
    nameInput.value = "";


    /*
     * Clear symbol.
     */
    const symbolInput =
        document.getElementById("newUnitSymbol");

    if (symbolInput) {
        symbolInput.value = "";
    }


    /*
     * Close modal.
     */
    closeUnitModal();
}


/* =====================================================
   LOCATION DROPDOWN
===================================================== */

function toggleLocationDropdown(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const card =
        document.getElementById("locationDropdownCard");

    if (!card) return;

    const isActive =
        card.classList.contains("active");

    closeAllPopups();

    if (!isActive) {
        card.classList.add("active");
    }
}


function toggleSelectAllLocations(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const checkboxes =
        document.querySelectorAll(
            ".location-checkbox"
        );

    if (!checkboxes.length) return;

    const allChecked =
        Array.from(checkboxes)
            .every(cb => cb.checked);

    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
}


function updateLocationSelection() {

    /*
     * Selection is applied when
     * the user clicks Apply.
     */
}


function applyLocationSelection(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const checkedBoxes =
        document.querySelectorAll(
            ".location-checkbox:checked"
        );

    const selectedValues =
        Array.from(checkedBoxes)
            .map(cb => cb.value);

    const hiddenInput =
        document.getElementById(
            "selectedLocationInput"
        );

    const displayLabel =
        document.getElementById(
            "locationDisplayLabel"
        );

    if (!hiddenInput || !displayLabel) {
        return;
    }


    if (selectedValues.length === 0) {

        displayLabel.textContent =
            "Select Location";

        hiddenInput.value = "";

    } else {

        displayLabel.textContent =
            selectedValues.join(", ");

        hiddenInput.value =
            selectedValues.join(",");
    }


    document
        .getElementById("locationDropdownCard")
        ?.classList.remove("active");
}


/* =====================================================
   CUSTOMER DROPDOWN
===================================================== */

function toggleCustomerDropdown(e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const popup =
        document.getElementById(
            "customerDropdownPopup"
        );

    if (!popup) return;

    const isActive =
        popup.classList.contains("active");

    closeAllPopups();

    if (!isActive) {
        popup.classList.add("active");
    }
}


function selectCustomer(name, code, e) {

    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    const input =
        document.getElementById(
            "customerSearchInput"
        );

    const hidden =
        document.getElementById(
            "selectedCustomerId"
        );

    if (input) {
        input.value =
            `${name} (${code})`;
    }

    if (hidden) {
        hidden.value = code;
    }

    document
        .getElementById(
            "customerDropdownPopup"
        )
        ?.classList.remove("active");
}


function filterCustomers() {

    const input =
        document.getElementById(
            "customerSearchInput"
        );

    if (!input) return;

    const filter =
        input.value.toLowerCase();

    const items =
        document.querySelectorAll(
            "#customerDropdownPopup .dropdown-option-item"
        );

    items.forEach(item => {

        item.style.display =
            item.textContent
                .toLowerCase()
                .includes(filter)
                ? "flex"
                : "none";
    });
}


/* =====================================================
   CLOSE ALL DROPDOWNS
===================================================== */

function closeAllPopups() {

    document
        .querySelectorAll(
            ".custom-dropdown-popup, " +
            ".location-dropdown-card, " +
            ".unit-dropdown-card"
        )
        .forEach(popup => {

            popup.classList.remove("active");
        });
}


/* =====================================================
   OUTSIDE CLICK
===================================================== */

document.addEventListener("click", function () {

    closeAllPopups();

});


/* =====================================================
   NAVIGATION
===================================================== */

function goBackToInvoices() {

    window.location.href =
        "/sales/invoice/";
}


function goBackToVariantProduct() {

    window.location.href =
        "/inventory/variant-product/";
}



/* =====================================================
   EXPORT SALES
===================================================== */

function toggleExportFields() {

    const checkbox =
        document.getElementById(
            "exportSalesToggle"
        );

    const fields =
        document.getElementById(
            "exportFieldsGroup"
        );

    if (checkbox && fields) {

        fields.style.display =
            checkbox.checked
                ? "grid"
                : "none";
    }
}


/* =====================================================
   TDS
===================================================== */

function toggleTdsFields() {

    const checkbox =
        document.getElementById(
            "tdsApplicableToggle"
        );

    const fields =
        document.getElementById(
            "tdsFieldsGroup"
        );

    if (checkbox && fields) {

        fields.style.display =
            checkbox.checked
                ? "grid"
                : "none";
    }
}


/* =====================================================
   VARIANT PRODUCT
===================================================== */


/*
 * Add a new Attribute / Option row.
 */
function addVariantAttributeRow() {

    const container =
        document.getElementById(
            "variantAttributesContainer"
        );

    if (!container) return;


    const rowDiv =
        document.createElement("div");

    rowDiv.className =
        "variant-attribute-row";


    rowDiv.innerHTML = `
        <div class="form-col invoice-form-group">

            <label>
                Attributes <span>*</span>
            </label>

            <select
                name="variant_attributes[]"
                class="variant-attribute-select"
                required
            >
                <option
                    value=""
                    disabled
                    selected
                >
                    Select Attributes
                </option>

                <option value="Color">
                    Color
                </option>

                <option value="Size">
                    Size
                </option>

                <option value="Material">
                    Material
                </option>
            </select>

        </div>

        <div class="form-col invoice-form-group">

            <label>
                Options <span>*</span>
            </label>

            <input
                type="text"
                name="variant_options[]"
                class="variant-option-input"
                placeholder="Please select or type (e.g. Red, Blue)"
                required
            >

        </div>

        <button
            type="button"
            class="remove-variant-row-btn"
            onclick="removeVariantAttributeRow(this)"
        >
            ✕
        </button>
    `;


    container.appendChild(rowDiv);

    hideVariantError();
}


/*
 * Remove an Attribute / Option row.
 */
function removeVariantAttributeRow(button) {

    const container =
        document.getElementById(
            "variantAttributesContainer"
        );

    if (!container) return;


    const rows =
        container.querySelectorAll(
            ".variant-attribute-row"
        );


    if (rows.length > 1) {

        const row =
            button.closest(
                ".variant-attribute-row"
            );

        if (row) {
            row.remove();
        }

    } else {

        showVariantError(
            "At least one attribute row is required."
        );
    }
}


/*
 * Validate inputs before generating variants.
 */
function generateVariants() {

    const attributeSelects =
        document.querySelectorAll(
            ".variant-attribute-select"
        );

    const optionInputs =
        document.querySelectorAll(
            ".variant-option-input"
        );

    let isValid = true;


    attributeSelects.forEach(
        (select, idx) => {

            const optVal =
                optionInputs[idx]
                    ? optionInputs[idx]
                        .value
                        .trim()
                    : "";

            if (!select.value || optVal === "") {
                isValid = false;
            }
        }
    );


    if (!isValid) {

        showVariantError(
            "Invalid variant configuration: " +
            "Please select an Attribute and fill in " +
            "Options for all rows before generating."
        );

        return false;
    }


    hideVariantError();

    alert(
        "Variants generated successfully!"
    );

    return true;
}


/*
 * Show variant error.
 */
function showVariantError(message) {

    const errElement =
        document.getElementById(
            "variantErrorMessage"
        );

    if (!errElement) return;

    errElement.innerText =
        message;

    errElement.style.display =
        "block";
}


/*
 * Hide variant error.
 */
function hideVariantError() {

    const errElement =
        document.getElementById(
            "variantErrorMessage"
        );

    if (!errElement) return;

    errElement.style.display =
        "none";
}