document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.querySelector('#saveButton');
    const saveSpinner = saveButton.querySelector('#Spinner');
    const saveButtonText = saveButton.querySelector('#ButtonText');
    const updateForm = document.querySelector('#UpdateSessionForm');
    const discardButton = document.querySelector('#discardButton');
    const inputFields = document.querySelectorAll('#UpdateSessionForm input');
    const editButton = document.querySelector('#EditButton');

    saveButton.addEventListener('click', function() {
        saveButton.disabled = true;
        saveSpinner.classList.remove('d-none');
        saveButtonText.classList.add('d-none');

        const formData = new FormData(updateForm);
        const sessionData = {};

        formData.forEach((value, key) => {
            if (key.startsWith('name_') || key.startsWith('start_date_') || key.startsWith('end_date_')) {
                sessionData[key] = value;
            }
        });

        const urlEncodedData = new URLSearchParams(sessionData).toString();

        fetch(updateForm.action, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: urlEncodedData
        })
        .then(response => response.json())
        .then(data => {
            saveButton.disabled = false;
            saveSpinner.classList.add('d-none');
            saveButtonText.classList.remove('d-none');

            if (data.success) {
                Swal.fire({
                    title: data.title,
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: data.confirmButtonText
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire(
                    data.message,
                    'error'
                );
            }
        })
        .catch(error => {
            console.error('Error:', error);
            saveButton.disabled = false;
            saveSpinner.classList.add('d-none');
            saveButtonText.classList.remove('d-none');

            Swal.fire(
                'Error!',
                'error'
            );
        });
    });

    inputFields.forEach(input => {
        input.addEventListener('input', () => {
            saveButton.disabled = false;
            discardButton.style.display = 'inline-block';
        });
    });

    editButton.addEventListener('click', () => {
        saveButton.disabled = false;  
    });

    discardButton.addEventListener('click', () => {
        location.reload();
    });
});
