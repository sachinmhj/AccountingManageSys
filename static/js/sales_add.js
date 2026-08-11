function openContactModal(mode = 'customer') {
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

    // Get all contact type buttons and their radios
    const typeButtons = document.querySelectorAll(".contact-type-btn");
    
    typeButtons.forEach(btn => {
        const radio = btn.querySelector('input[type="radio"]');
        if (!radio) return;

        // Check matching mode
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

    // Dynamically adjust Modal Title and Default Code Prefix based on mode
    if (mode === 'supplier') {
        if (modalTitle) modalTitle.textContent = "New Supplier";
        if (codeInput) codeInput.value = "S0001";
    } else if (mode === 'lead') {
        if (modalTitle) modalTitle.textContent = "New Lead";
        if (codeInput) codeInput.value = "L0001";
    } else {
        if (modalTitle) modalTitle.textContent = "New Customer";
        if (codeInput) codeInput.value = "C0002";
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
    
    // Prevent switching to disabled types
    if (radio && radio.disabled) return;

    const buttons = document.querySelectorAll(".contact-type-btn");
    buttons.forEach(btn => {
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

    if (contactName) {
        // Handle Payment Received dropdown update
        if (typeof selectReceivedFrom === "function") {
            selectReceivedFrom(contactName);
        }
        // Handle Invoice/Sales Order dropdown update
        else if (typeof selectCustomer === "function") {
            selectCustomer(contactName);
        }
        // Handle Purchase Bill / Supplier dropdown update
        else if (typeof selectSupplier === "function") {
            selectSupplier(contactName);
        }

        closeContactModal();

        const form = document.getElementById("newContactForm");
        if (form) {
            form.reset();
        }
    } else {
        alert("Please enter Name.");
    }
}