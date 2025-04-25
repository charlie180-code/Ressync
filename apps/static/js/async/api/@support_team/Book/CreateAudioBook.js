document.addEventListener('DOMContentLoaded', () => {
    const addAudiobookForm = document.querySelector('#addAudiobookModal form');

    if (addAudiobookForm) {
        addAudiobookForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(addAudiobookForm);
            const submitButton = event.target.querySelector('button[type="submit"]');
            const spinner = submitButton.querySelector('.spinner-border');
            const buttonText = submitButton.querySelector('#ButtonText');

            // Show spinner and hide text
            spinner.classList.remove('d-none');
            buttonText.classList.add('d-none');
            
            try {
                const response = await fetch(addAudiobookForm.action, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json()

                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: result.title,
                        text: result.message,
                        confirmButtonText: result.confirmButtonText
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: result.title,
                        text: result.message,
                        confirmButtonText: result.confirmButtonText
                    });
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                });
            } finally {
                // Hide spinner and show text
                spinner.classList.add('d-none');
                buttonText.classList.remove('d-none');
            }
        });
    }
});
