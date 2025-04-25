document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#createNewClassModal form');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());
        const action = form.action;

        try {
            document.getElementById('Spinner').classList.remove('d-none');
            document.getElementById('ButtonText').classList.add('d-none');

            const response = await fetch(action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData),
            });

            const result = await response.json();

            if (result.success) {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'success',
                    confirmButtonText: result.confirmButtonText
                }).then(() => {
                    location.reload(); 
                });
            } else {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'error',
                    confirmButtonText: result.confirmButtonText
                });
            }
        } catch (error) {
            Swal.fire({
                title: 'Error!',
                icon: 'error',
            });
        } finally {
            document.getElementById('Spinner').classList.add('d-none');
            document.getElementById('ButtonText').classList.remove('d-none');
        }
    });
});
