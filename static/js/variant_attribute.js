
    function openAttributeModal() {
        document.getElementById("attributeModalOverlay").style.display = "flex";
    }

    function closeAttributeModal() {
        document.getElementById("attributeModalOverlay").style.display = "none";
    }

    function addOptionRow() {
        const rowsContainer = document.getElementById("optionsListRows");
        const newRow = document.createElement("div");
        newRow.className = "option-row";
        newRow.innerHTML = `
            <input type="text" name="options[]" placeholder="Enter Options" required>
            <button type="button" class="btn-remove-option" onclick="removeOptionRow(this)">✕</button>
        `;
        rowsContainer.appendChild(newRow);
        newRow.querySelector("input").focus();
    }

    function removeOptionRow(btn) {
        const rows = document.querySelectorAll("#optionsListRows .option-row");
        if (rows.length > 1) {
            btn.parentElement.remove();
        } else {
            btn.previousElementSibling.value = "";
        }
    }

    function saveAttribute() {
        const form = document.getElementById("variantAttributeForm");
        if (form.checkValidity()) {
            form.submit();
        } else {
            form.reportValidity();
        }
    }
