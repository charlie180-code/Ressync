import UtilApiURLs from "../../../../../_globals/general/Archive.js";

document.addEventListener('DOMContentLoaded', function() {
    let rowCount = 0;

    const addRowBtn = document.getElementById('addRowBtn');
    const selectDeleteBtn = document.getElementById('selectDeleteBtn');
    const fileForm = document.getElementById('addFileForm');
    const folderSelect = document.querySelector('#DestinationFolderSelect');
    const submitButton = document.getElementById('submitButton');
    const buttonText = document.getElementById('buttonText');
    const loadingText = document.getElementById('AddfilesloadingText');

    addRowBtn.addEventListener('click', function() {
        rowCount++;
        const fileInputRows = document.querySelector('.file-input-rows');
        const newRow = document.createElement('div');
        const rowId = `row-${rowCount}`;
        newRow.id = rowId;
        newRow.classList.add('row', 'mb-3', 'align-items-end', 'file-input-row');
        newRow.innerHTML = `
            <div class="col">
                <label for="${rowId}-fileLabel" class="form-label">Label<span class="text-danger">*</span></label>
                <input type="text" id="${rowId}-fileLabel" name="labels[]" class="form-control" placeholder="Enter file label..." required>
            </div>
            <div class="col">
                <label for="${rowId}-fileInput" class="form-label">File<span class="text-danger">*</span></label>
                <input type="file" id="${rowId}-fileInput" name="files[]" class="form-control" required>
            </div>
            <div class="col-auto">
                <i class="bi bi-dash-circle remove-icon"></i>
            </div>
        `;
        fileInputRows.appendChild(newRow);
    });

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-icon')) {
            const rowToRemove = event.target.closest('.file-input-row');
            if (!rowToRemove.classList.contains('default-row')) {
                rowToRemove.remove();
            }
        }
    });

    selectDeleteBtn.addEventListener('click', function() {
        const fileInputRows = document.querySelectorAll('.file-input-row');
        fileInputRows.forEach(row => {
            if (!row.classList.contains('default-row')) {
                const removeIcon = row.querySelector('.remove-icon');
                removeIcon.style.display = 'inline-block';
            }
        });
    });

    fileForm.addEventListener('submit', function(event) {
        event.preventDefault();

        buttonText.style.display = 'inline-block';
        loadingText.style.display = 'none';
        submitButton.disabled = true;

        const formData = new FormData(fileForm);
        const folderId = folderSelect.value;
        const companyId = document.querySelector('#companyId').value;

        formData.append('folder_id', folderId);
        formData.append('company_id', companyId);

        fetch(`${UtilApiURLs.SaveFilesURL}/${folderId}/${companyId}`, {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            Swal.fire({
                icon: 'success',
                title: data.title,
                text: data.message,
                showConfirmButton: true,
                confirmButtonText: data.confirmButtonText
            }).then((result) => {
                if (result.isConfirmed) {
                    location.reload();
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message,
                showConfirmButton: true,
                confirmButtonText: 'OK'
            });
        })
        .finally(() => {
            buttonText.style.display = 'none';
            loadingText.style.display = 'inline-block';
            submitButton.disabled = false;
        });
    });
});
