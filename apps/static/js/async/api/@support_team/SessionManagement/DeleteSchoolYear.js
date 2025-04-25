document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const form = document.querySelector('#academicYearForm');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const yearId = button.getAttribute('data-year-id');
            const row = button.closest('tr');
            console.log(yearId);

            Swal.fire({
                title: 'Etes vous sûre?',
                text: "Ce changement est irréversible",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Oui, supprimer!',
                cancelButtonText: 'Annuler'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(form.action, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ year_id: yearId })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            row.remove();
                            Swal.fire({
                                title: 'Supprimée!',
                                text: data.message,
                                icon: 'success',
                                confirmButtonText: 'OK'
                            }).then(() => {
                                location.reload(); 
                            });
                        } else {
                            Swal.fire(
                                'Erreur!',
                                data.message,
                                'error'
                            );
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire(
                            'Erreur!',
                            'Une erreur s\'est produite lors de la supression',
                            'error'
                        );
                    });
                }
            });
        });
    });

});
