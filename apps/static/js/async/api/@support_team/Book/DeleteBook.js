document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.delete-book-form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            const bookId = this.getAttribute('data-book-id');
            const actionUrl = this.getAttribute('action');

            Swal.fire({
                title: 'Êtes-vous sûr ?',
                text: "Cette action supprimera le livre de la bibliothèque.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Oui, supprimer !',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(actionUrl, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 'Id': bookId })
                    }).then(response => {
                        const result = response.json()
                        if (response.ok) {
                            Swal.fire(
                                result.title,
                                result.message,
                                'success'
                            ).then(() => {
                                // Reload the page
                                location.reload();
                            });
                        } else {
                            Swal.fire(
                                result.title,
                                result.message,
                                result.confirmButtonText,
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
