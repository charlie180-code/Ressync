document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.edit-employee-form').forEach(form => {
        const employeeId = form.getAttribute('data-employee-id');
        const modal = document.getElementById(`editEmployeeModal${employeeId}`);
        const submitButton = modal.querySelector('#submitButton');
        const loadingSpinner = modal.querySelector('#loadingSpinner');
        const loadingText = modal.querySelector('#loadingText');
        const buttonText = modal.querySelector('#ButtonText');
        const draggableFileArea = modal.querySelector(".drag-file-area");
        const fileInput = modal.querySelector(".default-file-input");
        const uploadIcon = modal.querySelector(".upload-icon");
        const dragDropText = modal.querySelector("#dynamicMessage");
        const uploadedFile = modal.querySelector("#uploadedFileInfo");
        const profilePicInput = modal.querySelector(`#fileInput${employeeId}`);
        const fileName = modal.querySelector("#fileName");
        const fileSize = modal.querySelector("#fileSize");
        const progressBar = modal.querySelector("#progressBar");
        const removeFileButton = modal.querySelector(".remove-file-icon");

        const isAdvancedUpload = (() => {
            const div = document.createElement('div');
            return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 
                   'FormData' in window && 
                   'FileReader' in window;
        })();

        if (isAdvancedUpload) {
            ["drag", "dragstart", "dragend", "dragover", "dragenter", "dragleave", "drop"].forEach(evt => {
                draggableFileArea.addEventListener(evt, e => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            });

            ["dragover", "dragenter"].forEach(evt => {
                draggableFileArea.addEventListener(evt, () => {
                    uploadIcon.innerHTML = 'file_download';
                    dragDropText.innerHTML = 'Déposez vos fichiers ici';
                });
            });

            ["dragleave", "dragend"].forEach(evt => {
                draggableFileArea.addEventListener(evt, () => {
                    uploadIcon.innerHTML = 'file_upload';
                    dragDropText.innerHTML = 'Glissez vos fichiers ici';
                });
            });

            draggableFileArea.addEventListener("drop", e => {
                const files = e.dataTransfer.files;
                fileInput.files = files;
                handleFileSelection(files);
            });
        }

        fileInput.addEventListener("change", () => handleFileSelection(fileInput.files));

        function handleFileSelection(files) {
            if (files.length > 0) {
                uploadIcon.innerHTML = 'check_circle';
                dragDropText.innerHTML = 'Fichier ajouté!';
                fileName.textContent = files[0].name;
                fileSize.textContent = `${(files[0].size / 1024).toFixed(1)} KB`;
                uploadedFile.style.display = "flex";
                progressBar.style.transition = "width 0.5s ease-in-out";
                progressBar.style.width = "100%";
            }
        }

        removeFileButton.addEventListener("click", () => {
            uploadedFile.style.display = "none";
            fileInput.value = '';
            uploadIcon.innerHTML = 'file_upload';
            dragDropText.innerHTML = 'Glissez vos fichiers ici';
            fileName.textContent = '';
            fileSize.textContent = '';
            progressBar.style.width = "0%";
        });

        profilePicInput.addEventListener("change", () => {
            const file = profilePicInput.files[0];
            if (file) {
                const imgElement = modal.querySelector(`#employeeProfileImage${employeeId}`);
                const imgUrl = URL.createObjectURL(file);
                imgElement.src = imgUrl;
                imgElement.onload = () => URL.revokeObjectURL(imgUrl);
            }
        });

        form.addEventListener('submit', handleSubmit);

        function handleSubmit(e) {
            e.preventDefault();

            loadingSpinner.style.display = 'inline-block';
            loadingText.style.display = 'inline';
            buttonText.style.display = 'none';
            submitButton.disabled = true;

            const formData = new FormData(form);
            formData.append('employee_id', employeeId);

            const profilePicFile = profilePicInput.files[0];
            if (profilePicFile) {
                formData.append('profile_picture', profilePicFile);
            }

            const additionalFiles = fileInput.files;
            for (let i = 0; i < additionalFiles.length; i++) {
                formData.append('uploaded_files', additionalFiles[i]);
            }

            fetch(window.location.pathname, {
                method: 'PUT',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to submit form');
                }
                return response.json();
            })
            .then(data => {
                Swal.fire({
                    title: data.title,
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    window.location.reload();
                });
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    title: 'Erreur',
                    text: error.message || 'Une erreur est survenue lors de la mise à jour',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            })
            .finally(() => {
                loadingSpinner.style.display = 'none';
                loadingText.style.display = 'none';
                buttonText.style.display = 'inline';
                submitButton.disabled = false;
            });
        }
    });
});