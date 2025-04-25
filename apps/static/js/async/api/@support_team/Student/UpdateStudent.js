var isAdvancedUpload = function() {
    var div = document.createElement('div');
    return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
}();


document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('.edit-student-form');
    const submitButton = document.getElementById('submitButton');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingText = document.getElementById('loadingText');
    const buttonText = document.getElementById('ButtonText');

    const draggableFileArea = document.querySelector(".drag-file-area");
    const fileInput = document.querySelector(".default-file-input");
    const uploadIcon = document.querySelector(".upload-icon");
    const dragDropText = document.querySelector(".dynamic-message");
    const uploadedFile = document.querySelector(".file-block");
    const fileName = document.querySelector(".file-name");
    const fileSize = document.querySelector(".file-size");
    const progressBar = document.querySelector(".progress-bar");
    const removeFileButton = document.querySelector(".remove-file-icon");
    const profilePicInput = document.querySelector(`#fileInput${form.getAttribute('data-student-id')}`);
    let fileFlag = 0;

    profilePicInput.addEventListener("change", e => {
        const file = e.target.files[0];
        if (file) {
            const imgElement = document.getElementById(`profileImage${form.getAttribute('data-student-id')}`);
            imgElement.src = URL.createObjectURL(file);
        }
    });

    fileInput.addEventListener("change", e => {
        handleFileSelection(fileInput.files);
    });

    if (isAdvancedUpload) {
        ["drag", "dragstart", "dragend", "dragover", "dragenter", "dragleave", "drop"].forEach(evt =>
            draggableFileArea.addEventListener(evt, e => {
                e.preventDefault();
                e.stopPropagation();
            })
        );

        ["dragover", "dragenter"].forEach(evt => {
            draggableFileArea.addEventListener(evt, e => {
                e.preventDefault();
                e.stopPropagation();
                uploadIcon.innerHTML = 'file_download';
                dragDropText.innerHTML = 'Glissez vos fichiers ici';
            });
        });

        draggableFileArea.addEventListener("drop", e => {
            e.preventDefault();
            e.stopPropagation();
            const files = e.dataTransfer.files;
            handleFileSelection(files);
        });
    }

    function handleFileSelection(files) {
        if (files.length > 0) {
            uploadedFile.style.display = "flex";
            fileName.innerHTML = files[0].name;
            fileSize.innerHTML = (files[0].size / 1024).toFixed(1) + " KB";
            uploadIcon.innerHTML = 'check_circle';
            dragDropText.innerHTML = 'Fichier ajouté!';
            progressBar.style.width = 0;
            fileFlag = 0;
            fileInput.files = files;
        }
    }

    removeFileButton.addEventListener("click", () => {
        uploadedFile.style.display = "none";
        fileInput.value = '';
        uploadIcon.innerHTML = 'file_upload';
        dragDropText.innerHTML = 'Glissez vos fichiers ici';
        fileName.innerHTML = '';
        fileSize.innerHTML = '';
        progressBar.style.width = 0;
        fileFlag = 0;
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
    
        loadingSpinner.style.display = 'inline-block';
        loadingText.style.display = 'inline';
        buttonText.style.display = 'none';
        submitButton.disabled = true;
    
        const formData = new FormData(form);
    
        const profilePicFile = profilePicInput.files[0];
        if (profilePicFile) {
            formData.append('profile_picture', profilePicFile);
        }
    
        const companyId = form.getAttribute('data-company-id');
        const studentId = form.getAttribute('data-student-id');
        const userId = form.getAttribute('data-user-id');
    
        formData.append('company_id', companyId);
        formData.append('student_id', studentId);
        formData.append('user_id', userId);
    
        const additionalFiles = fileInput.files;
        for (let i = 0; i < additionalFiles.length; i++) {
            formData.append('uploaded_file', additionalFiles[i]);
        }
    
        fetch(window.location.pathname, {
            method: 'PUT',
            body: formData 
        })
        .then(response => {
            if (response.ok) {
                return response.blob(); 
            } else {
                return response.json().then(result => {
                    throw new Error(result.error); 
                });
            }
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'invoice.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
    
            Swal.fire({
                title: 'Mise à jour effectuée',
                text: 'Les informations de l\'étudiant ont été mises à jour avec succès!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                window.location.reload(); 
            });
        })
        .catch(error => {
            Swal.fire({
                title: 'Erreur',
                text: error.message,
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
    });    
});
