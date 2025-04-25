document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-audiobook-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            const audiobookId = this.getAttribute('data-audiobook-id');
            const actionUrl = this.getAttribute('action');

            Swal.fire({
                title: 'Etes-vous sure?',
                text: "Cette action va supprimer le livre de la base de données",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Oui, supprimer!',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(actionUrl, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 'id': audiobookId })
                    }).then(response => {
                        
                        const result = response.json()

                        if (response.ok) {
                            Swal.fire(
                                result.title,
                                result.message,
                                'success'
                            ).then(() => {
                                location.reload();
                            });
                        } else {
                            Swal.fire(
                                result.title,
                                result.message,
                                'error'
                            );
                        }
                    }).catch(error => {
                        console.error('Error:', error);
                        Swal.fire(
                            'Error!',
                            'error'
                        );
                    });
                }
            });
        });
    });
});
