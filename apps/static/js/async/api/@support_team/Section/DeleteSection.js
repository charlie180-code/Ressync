document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const sectionId = this.getAttribute('data-section-id');

            Swal.fire({
                title: 'Êtes-vous sûr(e) ?',
                text: "Vous ne pourrez pas annuler cette action !",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(window.location.pathname, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({'sectionId': sectionId})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.querySelector(`tr[data-section-id="${sectionId}"]`).remove();

                            Swal.fire({
                                icon: 'success',
                                title: data.title,
                                text: data.message,
                                confirmButtonText: data.confirmButtonText
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: data.title,
                                text: data.message,
                                confirmButtonText: data.confirmButtonText
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);

                        Swal.fire({
                            icon: 'error',
                            title: 'Error!'
                        });
                    });
                }
            });
        });
    });
});