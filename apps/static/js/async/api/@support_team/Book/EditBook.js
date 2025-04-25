document.addEventListener('DOMContentLoaded', () => {
    const editBookForms = document.querySelectorAll('.modal form');

    editBookForms.forEach(form => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(form);
            const bookId = form.querySelector('[name="id"]').value;
            formData.append('id', bookId);

            const spinner = form.querySelector('.spinner');
            const buttonText = form.querySelector('.ButtonText'); // Use a more generic class to target the correct element

            spinner.classList.remove('d-none');
            buttonText.classList.add('d-none');

            try {
                const response = await fetch(form.action, {
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
                    title: 'Error!'
                });
            } finally {
                spinner.classList.add('d-none');
                buttonText.classList.remove('d-none');
            }
        });
    });
});
