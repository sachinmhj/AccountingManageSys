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

    if (typeof selectReceivedFrom === "function") {
        selectReceivedFrom(contactName);
    } else if (typeof selectCustomer === "function") {
        selectCustomer(contactName);
    } else if (typeof selectSupplier === "function") {
        selectSupplier(contactName);
    }

    closeContactModal();

    const form = document.getElementById("newContactForm");
    if (form) {
        form.reset();
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