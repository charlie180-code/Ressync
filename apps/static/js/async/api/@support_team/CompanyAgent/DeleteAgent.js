document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', function () {
            const adminId = this.getAttribute('data-admin-id');
            const companyId = this.getAttribute('data-company-id');

            Swal.fire({
                title: 'Êtes-vous sûr?',
                text: "Vous ne pourrez pas annuler cela!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Oui, supprimer!'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(window.location.pathname, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ user_id: adminId })
                    })
                    .then(response => response.json())
                    .then(data => {
                        Swal.fire({
                            title: data.title,
                            text: data.message || data.error,
                            icon: data.error ? 'error' : 'success',
                            confirmButtonText: data.confirmButtonText
                        }).then(() => {
                            if (!data.error) {
                                location.reload();
                            }
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                }
            });
        });
    });
});
