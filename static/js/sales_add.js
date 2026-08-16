function openContactModal(mode = "customer") {
    const receivedDropdown = document.getElementById("receivedFromDropdownMenu");
    if (receivedDropdown) {
        receivedDropdown.style.display = "none";
    }

    const customerDropdown = document.getElementById("customerDropdownPopup");
    if (customerDropdown) {
        customerDropdown.classList.remove("active");
    }

    const modalTitle = document.querySelector("#contactModalOverlay .modal-header h3");
    const codeInput = document.querySelector('input[name="contact_code"]');
    const typeButtons = document.querySelectorAll(".contact-type-btn");

    typeButtons.forEach(function (btn) {
        const radio = btn.querySelector('input[type="radio"]');
        if (!radio) {
            return;
        }

        if (radio.value === mode) {
            btn.classList.add("active");
            btn.classList.remove("disabled");
            radio.disabled = false;
            radio.checked = true;
        } else {
            btn.classList.remove("active");
            btn.classList.add("disabled");
            radio.disabled = true;
            radio.checked = false;
        }
    });

    if (mode === "supplier") {
        if (modalTitle) {
            modalTitle.textContent = "New Supplier";
        }
        if (codeInput) {
            codeInput.value = "S0001";
        }
    } else if (mode === "lead") {
        if (modalTitle) {
            modalTitle.textContent = "New Lead";
        }
        if (codeInput) {
            codeInput.value = "L0001";
        }
    } else {
        if (modalTitle) {
            modalTitle.textContent = "New Customer";
        }
        if (codeInput) {
            codeInput.value = "C0002";
        }
    }

    const modal = document.getElementById("contactModalOverlay");
    if (modal) {
        modal.style.display = "flex";
    } else {
        console.error("contactModalOverlay not found");
    }
}

function closeContactModal() {
    const modal = document.getElementById("contactModalOverlay");
    if (modal) {
        modal.style.display = "none";
    }
}

function selectContactType(element, typeValue) {
    const radio = element.querySelector('input[type="radio"]');
    if (radio && radio.disabled) {
        return;
    }

    const buttons = document.querySelectorAll(".contact-type-btn");
    buttons.forEach(function (btn) {
        const btnRadio = btn.querySelector('input[type="radio"]');
        if (btnRadio && !btnRadio.disabled) {
            btn.classList.remove("active");
            btnRadio.checked = false;
        }
    });

    element.classList.add("active");
    if (radio) {
        radio.checked = true;
    }
}

function saveNewContact() {
    const nameInput = document.getElementById("contactNameInput");
    const contactName = nameInput ? nameInput.value.trim() : "";

    if (!contactName) {
        alert("Please enter Name.");
        return;
    }

    let isPicker = false;

    // Handle Payment Received dropdown update
    if (typeof selectReceivedFrom === "function") {
        selectReceivedFrom(contactName);
        isPicker = true;
    }
    // Handle Invoice/Sales Order dropdown update
    else if (typeof selectCustomer === "function") {
        selectCustomer(contactName);
        isPicker = true;
    }
    // Handle Purchase Bill / Supplier dropdown update
    else if (typeof selectSupplier === "function") {
        selectSupplier(contactName);
        isPicker = true;
    }

    if (isPicker) {
        closeContactModal();
        const form = document.getElementById("newContactForm");
        if (form) {
            form.reset();
        }
    } else {
        // We are on the Customers list page, so actually submit to backend
        const form = document.getElementById("newContactForm");
        if (form) {
            form.submit();
        }
    }
}

function openProductAddPopup() {
    const modal = document.getElementById("productAddOverlay");
    if (modal) {
        modal.style.display = "flex";
    } else {
        console.error("productAddOverlay not found");
    }
}

function closeProductAddPopup() {
    const modal = document.getElementById("productAddOverlay");
    if (modal) {
        modal.style.display = "none";
        const form = document.getElementById("newProductForm");
        if (form) {
            form.reset();
        }
    }
}

function setProductType(type) {
    const productTypeInput = document.getElementById("productTypeInput");
    const btnGoods = document.getElementById("typeBtnGoods");
    const btnServices = document.getElementById("typeBtnServices");

    if (productTypeInput) {
        productTypeInput.value = type;
    }

    if (type === "Goods") {
        if (btnGoods) {
            btnGoods.classList.add("active");
        }
        if (btnServices) {
            btnServices.classList.remove("active");
        }
    } else {
        if (btnServices) {
            btnServices.classList.add("active");
        }
        if (btnGoods) {
            btnGoods.classList.remove("active");
        }
    }
}

window.addEventListener("click", function (event) {
    const contactModal = document.getElementById("contactModalOverlay");
    if (contactModal && event.target === contactModal) {
        closeContactModal();
    }

    const productModal = document.getElementById("productAddOverlay");
    if (productModal && event.target === productModal) {
        closeProductAddPopup();
    }
});

document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") {
        return;
    }

    const contactModal = document.getElementById("contactModalOverlay");
    if (contactModal && contactModal.style.display === "flex") {
        closeContactModal();
    }

    const productModal = document.getElementById("productAddOverlay");
    if (productModal && productModal.style.display === "flex") {
        closeProductAddPopup();
    }
});

/* =====================================================
   PRODUCT PICKER & ROW LOGIC
===================================================== */
function toggleProductPickerDropdown(e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    const popup = document.getElementById("productPickerDropdownPopup");
    if (!popup) return;
    
    if (typeof closeAllPopups === 'function') {
        closeAllPopups();
    }
    
    popup.classList.toggle("active");
}

function filterProductsPicker() {
    const input = document.getElementById("productSearchInput");
    if (!input) return;
    const filter = input.value.toUpperCase();
    const list = document.getElementById("productPickerOptionsList");
    if (!list) return;
    
    const items = list.querySelectorAll(".dropdown-option-item");
    items.forEach(item => {
        const txtValue = item.textContent || item.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            item.style.display = "";
        } else {
            item.style.display = "none";
        }
    });
}

function selectProductRow(productId, e) {
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    const popup = document.getElementById("productPickerDropdownPopup");
    if (popup) {
        popup.classList.remove("active");
    }
    
    const input = document.getElementById("productSearchInput");
    if (input) {
        input.value = ""; 
        filterProductsPicker(); 
    }
    
    const product = typeof availableProducts !== 'undefined' ? availableProducts[productId] : null;
    if (!product) return;
    
    appendProductRow(productId, product);
}

function appendProductRow(productId, product) {
    const container = document.getElementById("invoiceItemsContainer");
    if (!container) return;
    
    const rowId = 'row_' + Math.random().toString(36).substr(2, 9);
    
    const rowHTML = `
        <div class="invoice-item-row-data" id="${rowId}">
            <input type="hidden" name="product_id[]" value="${productId}">
            
            <div class="item-col product-col">
                <div class="item-product-name">${product.name}</div>
                <div class="item-product-meta">
                    <a href="javascript:void(0)" onclick="viewProductDetails('${productId}')">View Details</a>
                </div>
            </div>
            
            <div class="item-col qty-col">
                <input type="number" name="qty[]" value="1" min="1" oninput="calculateRowAmount('${rowId}')">
            </div>
            
            <div class="item-col rate-col">
                <input type="number" name="rate[]" value="${product.selling_price}" step="0.01" oninput="calculateRowAmount('${rowId}')">
            </div>
            
            <div class="item-col discount-col">
                <input type="number" name="discount[]" value="0" step="0.01" oninput="calculateRowAmount('${rowId}')">
                <select name="discount_type[]" onchange="calculateRowAmount('${rowId}')">
                    <option value="%">%</option>
                    <option value="Flat">Flat</option>
                </select>
            </div>
            
            <div class="item-col tax-col">
                <select name="tax[]" onchange="calculateRowAmount('${rowId}')">
                    <option value="0">0 VAT</option>
                    <option value="13">13 VAT</option>
                </select>
            </div>
            
            <div class="item-col amount-col">
                <span class="row-amount-display">-</span>
                <input type="hidden" name="amount[]" class="row-amount-input" value="0">
            </div>
            
            <div class="item-col action-col">
                <button type="button" class="remove-row-btn" onclick="removeProductRow('${rowId}')">×</button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', rowHTML);
    calculateRowAmount(rowId);
}

function removeProductRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        row.remove();
        calculateTotals();
    }
}

function calculateRowAmount(rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;
    
    const qty = parseFloat(row.querySelector('input[name="qty[]"]').value) || 0;
    const rate = parseFloat(row.querySelector('input[name="rate[]"]').value) || 0;
    let discount = parseFloat(row.querySelector('input[name="discount[]"]').value) || 0;
    const discountType = row.querySelector('select[name="discount_type[]"]').value;
    
    let baseAmount = qty * rate;
    
    if (discountType === '%') {
        discount = baseAmount * (discount / 100);
    }
    
    let afterDiscount = baseAmount - discount;
    if (afterDiscount < 0) afterDiscount = 0;
    
    const display = row.querySelector('.row-amount-display');
    const input = row.querySelector('.row-amount-input');
    
    display.textContent = afterDiscount > 0 ? afterDiscount.toFixed(2) : '-';
    input.value = afterDiscount.toFixed(2);
    
    calculateTotals();
}

function calculateTotals() {
    let sumAfterItemDiscounts = 0;
    let taxableBase = 0;
    let nonTaxableBase = 0;
    
    const rows = document.querySelectorAll('.invoice-item-row-data');
    const header = document.getElementById("invoiceItemsHeader");
    const summary = document.getElementById("invoiceSummarySection");
    
    if (rows.length > 0) {
        if (summary) summary.style.display = "block";
    } else {
        if (summary) summary.style.display = "none";
    }
    
    rows.forEach(row => {
        const qty = parseFloat(row.querySelector('input[name="qty[]"]').value) || 0;
        const rate = parseFloat(row.querySelector('input[name="rate[]"]').value) || 0;
        let discount = parseFloat(row.querySelector('input[name="discount[]"]').value) || 0;
        const discountType = row.querySelector('select[name="discount_type[]"]').value;
        const taxPercent = parseFloat(row.querySelector('select[name="tax[]"]').value) || 0;
        
        let baseAmount = qty * rate;
        if (discountType === '%') {
            discount = baseAmount * (discount / 100);
        }
        
        let afterItemDiscount = baseAmount - discount;
        if (afterItemDiscount < 0) afterItemDiscount = 0;
        
        sumAfterItemDiscounts += afterItemDiscount;
        
        if (taxPercent > 0) {
            taxableBase += afterItemDiscount;
        } else {
            nonTaxableBase += afterItemDiscount;
        }
    });
    
    // Global discount
    const globalDiscInput = document.getElementById("globalDiscountInput");
    const globalDiscType = document.getElementById("globalDiscountType");
    let globalDiscount = 0;
    if (globalDiscInput && globalDiscType) {
        let discVal = parseFloat(globalDiscInput.value) || 0;
        if (globalDiscType.value === '%') {
            globalDiscount = sumAfterItemDiscounts * (discVal / 100);
        } else {
            globalDiscount = discVal;
        }
    }
    
    // Distribute global discount proportionally to taxable and non-taxable
    let propTaxable = sumAfterItemDiscounts > 0 ? (taxableBase / sumAfterItemDiscounts) : 0;
    let propNonTaxable = sumAfterItemDiscounts > 0 ? (nonTaxableBase / sumAfterItemDiscounts) : 0;
    
    let finalTaxable = taxableBase - (globalDiscount * propTaxable);
    let finalNonTaxable = nonTaxableBase - (globalDiscount * propNonTaxable);
    
    if (finalTaxable < 0) finalTaxable = 0;
    if (finalNonTaxable < 0) finalNonTaxable = 0;
    
    let vatAmount = finalTaxable * 0.13;
    
    const grandTotal = finalTaxable + finalNonTaxable + vatAmount;
    
    // Display values
    const subTotalDisplay = document.getElementById("subTotalDisplay");
    if (subTotalDisplay) subTotalDisplay.textContent = sumAfterItemDiscounts > 0 ? sumAfterItemDiscounts.toFixed(2) : '-';
    
    const globalDiscountDisplay = document.getElementById("globalDiscountDisplay");
    if (globalDiscountDisplay) globalDiscountDisplay.textContent = globalDiscount > 0 ? '-' + globalDiscount.toFixed(2) : '-';
    
    const nonTaxableDisplay = document.getElementById("nonTaxableTotalDisplay");
    if (nonTaxableDisplay) nonTaxableDisplay.textContent = finalNonTaxable > 0 ? finalNonTaxable.toFixed(2) : '-';
    
    const taxableDisplay = document.getElementById("taxableTotalDisplay");
    if (taxableDisplay) taxableDisplay.textContent = finalTaxable > 0 ? finalTaxable.toFixed(2) : '-';
    
    const vatDisplay = document.getElementById("vatTotalDisplay");
    if (vatDisplay) vatDisplay.textContent = vatAmount > 0 ? vatAmount.toFixed(2) : '-';
    
    const totalDisplay = document.getElementById("grandTotalDisplay");
    if (totalDisplay) totalDisplay.textContent = grandTotal > 0 ? grandTotal.toFixed(2) : '-';
}

function viewProductDetails(productId) {
    const product = typeof availableProducts !== 'undefined' ? availableProducts[productId] : null;
    if (!product) return;
    
    document.getElementById("offcanvasProductName").textContent = product.name;
    document.getElementById("offcanvasProductCategory").textContent = product.category || 'N/A';
    document.getElementById("offcanvasSellingPrice").textContent = 'Rs ' + product.selling_price;
    document.getElementById("offcanvasPurchasePrice").textContent = 'Rs ' + product.purchase_price;
    document.getElementById("offcanvasCategoryName").textContent = product.category || 'N/A';
    document.getElementById("offcanvasProductAvatar").textContent = product.name.charAt(0).toUpperCase();
    
    document.getElementById("productDetailsOffcanvas").classList.add("active");
    document.getElementById("productDetailsOverlay").classList.add("active");
}

function closeProductDetails() {
    document.getElementById("productDetailsOffcanvas").classList.remove("active");
    document.getElementById("productDetailsOverlay").classList.remove("active");
}