document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#createNewAcademicYearModal form');
    const submitButton = form.querySelector('button[type="submit"]');
    const spinner = submitButton.querySelector('#Spinner');
    const buttonText = submitButton.querySelector('#ButtonText');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const yearData = Object.fromEntries(formData.entries());

        submitButton.disabled = true;
        spinner.classList.remove('d-none');
        buttonText.classList.add('d-none');

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(yearData)
        })
        .then(response => response.json())
        .then(data => {
            submitButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.classList.remove('d-none');

            if (data.success) {
                Swal.fire({
                    title:data.title,
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
            submitButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.classList.remove('d-none');

            Swal.fire(
                'Error!',
                'error'
            );
        });
    });
});
