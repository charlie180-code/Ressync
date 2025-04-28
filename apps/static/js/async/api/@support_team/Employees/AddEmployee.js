
import domain from "../../../../_globals/domain.js";

const companyId = document.querySelector('#company-id').value;

document.getElementById('createEmployeeProfilePic').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const placeholder = document.getElementById('createEmployeePlaceholder');
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.className = 'profile-image rounded-circle';
        img.onload = function() {
            URL.revokeObjectURL(img.src);
        }
        placeholder.replaceWith(img);
    }
});

const createEmployeeFileInput = document.getElementById('createEmployeeFiles');
const createEmployeeUploadedFiles = document.getElementById('createEmployeeUploadedFiles');
const createEmployeeFileName = document.getElementById('createEmployeeFileName');
const createEmployeeFileSize = document.getElementById('createEmployeeFileSize');

createEmployeeFileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        createEmployeeFileName.textContent = this.files[0].name;
        createEmployeeFileSize.textContent = `${(this.files[0].size / 1024).toFixed(1)} KB`;
        createEmployeeUploadedFiles.style.display = "flex";
    }
});

document.querySelector('#createEmployeeUploadedFiles .remove-file-icon').addEventListener('click', function() {
    createEmployeeFileInput.value = '';
    createEmployeeUploadedFiles.style.display = "none";
});

document.getElementById('createEmployeeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('createEmployeeSubmit');
    const spinner = document.getElementById('createEmployeeSpinner');
    
    submitBtn.disabled = true;
    spinner.style.display = 'inline-block';
    
    const formData = new FormData(this);
    
    const profilePic = document.getElementById('createEmployeeProfilePic').files[0];
    if (profilePic) {
        formData.append('profile_picture', profilePic);
    }
    
    const additionalFiles = document.getElementById('createEmployeeFiles').files;
    for (let i = 0; i < additionalFiles.length; i++) {
        formData.append('uploaded_files', additionalFiles[i]);
    }
    
    fetch(`${domain}/career/v1/employees/${companyId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'Accept': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            Swal.fire({
                title: data.title,
                text: data.message,
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                window.location.reload();
            });
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        Swal.fire({
            title: 'Error',
            text: error.message,
            icon: 'error',
            confirmButtonText: 'OK'
        });
    })
    .finally(() => {
        submitBtn.disabled = false;
        spinner.style.display = 'none';
    });
});