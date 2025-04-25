document.addEventListener('DOMContentLoaded', function() {
    const createForm = document.querySelector('#createNewSessionModal form');
    const createSubmitButton = createForm.querySelector('button[type="submit"]');
    const createSpinner = createSubmitButton.querySelector('#Spinner');
    const createButtonText = createSubmitButton.querySelector('#ButtonText');

    createForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(createForm);
        const sessionData = Object.fromEntries(formData.entries());

        createSubmitButton.disabled = true;
        createSpinner.classList.remove('d-none');
        createButtonText.classList.add('d-none');

        fetch(createForm.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sessionData)
        })
        .then(response => response.json())
        .then(data => {
            createSubmitButton.disabled = false;
            createSpinner.classList.add('d-none');
            createButtonText.classList.remove('d-none');

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
                    'Error!',
                    data.message,
                    'error'
                );
            }
        })
        .catch(error => {
            console.error('Error:', error);
            createSubmitButton.disabled = false;
            createSpinner.classList.add('d-none');
            createButtonText.classList.remove('d-none');

            Swal.fire(
                'Error!',
                'error'
            );
        });
    });
});
