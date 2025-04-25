document.addEventListener("DOMContentLoaded", function() {
    const sectionTableBody = document.querySelector("tbody");
    const saveButton = document.getElementById("saveButton");
    const discardButton = document.getElementById("discardButton");
    const spinner = document.getElementById("Spinner");
    const buttonText = document.getElementById("ButtonText");
    const loadingText = document.getElementById("LoadingText");

    let initialSectionState = {};

    sectionTableBody.querySelectorAll("tr").forEach((row, index) => {
        const sectionNameCell = row.querySelector(".editable-cell");
        initialSectionState[index] = {
            name: sectionNameCell.innerText.trim(),
            created_at: row.cells[2].innerText.trim()
        };
    });

    sectionTableBody.addEventListener("input", function() {
        saveButton.style.display = "inline-block";
        discardButton.style.display = "inline-block";
        saveToLocalStorage();
    });

    saveButton.addEventListener("click", async function() {
        saveButton.disabled = true;
        spinner.classList.remove("d-none");
        buttonText.classList.add("d-none");
        loadingText.classList.remove("d-none");

        const rows = sectionTableBody.querySelectorAll("tr");
        const data = [];

        rows.forEach((row, index) => {
            const sectionNameCell = row.querySelector(".editable-cell");
            const sectionName = sectionNameCell.innerText.trim();
            const sectionId = row.getAttribute("data-section-id");
            const createdAt = row.cells[2].innerText.trim();

            if (sectionName !== initialSectionState[index].name || createdAt !== initialSectionState[index].created_at) {
                data.push({
                    id: sectionId,
                    name: sectionName,
                    created_at: createdAt
                });
            }
        });

        try {
            const response = await fetch(document.getElementById('sectionEditForm').action, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'success',
                    confirmButtonText: result.confirmButtonText
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.reload();
                    }
                });
                saveButton.style.display = "none";
                discardButton.style.display = "none";
                localStorage.removeItem('sectionData');
            } else {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'error'
                });
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error!',
                icon: 'error'
            });
        } finally {
            saveButton.disabled = false;
            spinner.classList.add("d-none");
            buttonText.classList.remove("d-none");
            loadingText.classList.add("d-none");
        }
    });

    discardButton.addEventListener("click", function() {
        sectionTableBody.querySelectorAll("tr").forEach((row, index) => {
            const sectionNameCell = row.querySelector(".editable-cell");
            sectionNameCell.innerText = initialSectionState[index].name;
            row.cells[2].innerText = initialSectionState[index].created_at;
        });
        saveButton.style.display = "none";
        discardButton.style.display = "none";
        localStorage.removeItem('sectionData');
    });

    function saveToLocalStorage() {
        const rows = sectionTableBody.querySelectorAll("tr");
        const data = [];

        rows.forEach((row) => {
            const sectionNameCell = row.querySelector(".editable-cell");
            const sectionName = sectionNameCell.innerText.trim();
            const createdAt = row.cells[2].innerText.trim();
            const sectionId = row.getAttribute("data-section-id");

            data.push({
                id: sectionId,
                name: sectionName,
                created_at: createdAt
            });
        });

        localStorage.setItem('sectionData', JSON.stringify(data));
    }
});
