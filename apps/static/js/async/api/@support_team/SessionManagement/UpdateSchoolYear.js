document.addEventListener('DOMContentLoaded', () => {
    const saveButton = document.getElementById('saveButton');
    const discardButton = document.getElementById('discardButton');
    const editButton = document.getElementById('editButton');
    const spinner = document.getElementById('Spinner');
    const buttonText = document.getElementById('ButtonText');
    let originalData = {};

    editButton.addEventListener('click', () => {
        saveButton.disabled = false;
        discardButton.style.display = 'inline-block';
        document.querySelectorAll('input[type="text"], input[type="date"]').forEach(input => {
            const id = input.id;
            originalData[id] = input.value;
        });
    });

    // Save changes
    saveButton.addEventListener('click', () => {
        Swal.fire({
            title: 'Êtes-vous sûr?',
            text: "Vous voulez sauvegarder les modifications?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Oui, sauvegarder',
            cancelButtonText: 'Annuler',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {
                saveButton.disabled = true;
                spinner.classList.remove('d-none');
                buttonText.textContent = 'Enregistrement...';

                // Collect updated data
                const formData = new FormData(document.getElementById('academicYearForm'));

                fetch(document.getElementById('academicYearForm').action, {
                    method: 'PUT',
                    body: formData,
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire(data.message, 'success');
                    } else {
                        Swal.fire('Error!', 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Error!', 'error');
                })
                .finally(() => {
                    spinner.classList.add('d-none');
                    buttonText.textContent = 'Enregistrer';
                    saveButton.disabled = false;
                });
            }
        });
    });

    // Revert changes
    discardButton.addEventListener('click', () => {
        Swal.fire({
            title: 'Êtes-vous sûr?',
            text: "Vous voulez annuler les modifications?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Oui, annuler',
            cancelButtonText: 'Non',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {
                document.querySelectorAll('input[type="text"], input[type="date"]').forEach(input => {
                    const id = input.id;
                    if (originalData[id]) {
                        input.value = originalData[id];
                    }
                });

                saveButton.disabled = true;
                discardButton.style.display = 'none';
            }
        });
    });
});
