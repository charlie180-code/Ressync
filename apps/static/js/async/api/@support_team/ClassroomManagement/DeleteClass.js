document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const updateClassForm = document.getElementById('UpdateClassForm');

    deleteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const classId = button.getAttribute('data-class-id');

            Swal.fire({
                title: 'Êtes-vous sûr ?',
                text: "Cette action ne peut pas être annulée.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Oui, supprimer',
                cancelButtonText: 'Non, annuler'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const response = await fetch(updateClassForm.action, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ id: classId })
                        });

                        const result = await response.json();

                        if (response.ok) {
                            Swal.fire({
                                title: result.title,
                                text: result.title,
                                icon: 'success',
                                confirmButtonText: result.confirmButtonText
                            }).then(() => {
                                location.reload();
                            });
                        } 
                    } catch (error) {
                        console.error('Erreur:', error);
                        Swal.fire({
                            title: 'Error!',
                            icon: 'error'
                        });
                    }
                }
            });
        });
    });
});
