document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('newTeacherForm');
    const spinner = document.getElementById('Spinner');
    const buttonText = document.getElementById('ButtonText');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        spinner.classList.remove('d-none');
        buttonText.classList.add('d-none');

        const formData = new FormData(form);
        const data = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            email: formData.get('email'),
            wage: formData.get('wage'),
            wage_system: formData.get('wage_system'),
            currency: formData.get('currency'),
            session_id: formData.get('session_id')
        };

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    text: result.message,
                }).then(() => {
                    location.reload();
                });
                form.reset();
            } else {
                Swal.fire({
                    icon: 'error',
                    text: result.message,
                });
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error!',
            });
        } finally {
            spinner.classList.add('d-none');
            buttonText.classList.remove('d-none');
        }
    });
});
