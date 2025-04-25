document.addEventListener('DOMContentLoaded', function () {
    const editFolderForms = document.querySelectorAll('.editFolderForm');

    editFolderForms.forEach(form => {
        form.addEventListener('submit', async function (event) {
            event.preventDefault();
            const folderId = this.dataset.folderId;

            const formData = new FormData(this);
            const data = {
                id: folderId,
                description: formData.get('description'),
                type: formData.get('type'),
                client: formData.get('client'),
                transport: formData.get('transport'),
                weight: formData.get('weight'),
                bills_of_ladding: formData.get('bills_of_ladding'),
                deadline: formData.get('deadline')
            };

            try {
                const response = await fetch(this.action, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: data.title,
                        text: data.message,
                        confirmButtonText: data.confirmButtonText
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: result.message
                    });

                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error'
                });
            }
        });
    });
});
