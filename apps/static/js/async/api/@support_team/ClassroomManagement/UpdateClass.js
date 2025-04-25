document.addEventListener('DOMContentLoaded', () => {
    const updateClassForm = document.getElementById('UpdateClassForm');
    const saveButton = document.getElementById('saveButton');
    const discardButton = document.getElementById('discardButton');
    const spinner = document.getElementById('Spinner');
    const buttonText = document.getElementById('ButtonText');

    saveButton.disabled = true;
    discardButton.style.display = 'none';

    updateClassForm.addEventListener('change', () => {
        saveButton.disabled = false;
        discardButton.style.display = 'inline-block';
    });

    discardButton.addEventListener('click', () => {
        Swal.fire({
            title: 'Êtes-vous sûr ?',
            text: "Tous les changements non enregistrés seront perdus.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Oui, annuler',
            cancelButtonText: 'Non'
        }).then((result) => {
            if (result.isConfirmed) {
                location.reload();
            }
        });
    });

    updateClassForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        saveButton.disabled = true;
        spinner.classList.remove('d-none');
        buttonText.textContent = 'Enregistrement...';

        try {
            const formData = new FormData(updateClassForm);
            const response = await fetch(updateClassForm.action, {
                method: 'PUT',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'success',
                    confirmButtonText: result.confirmButtonText
                }).then(() => {
                    location.reload();
                });
            } 
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error!',
                icon: 'error'
            });
        } finally {
            spinner.classList.add('d-none');
            buttonText.textContent = 'Enregistrer';
        }
    });
});
