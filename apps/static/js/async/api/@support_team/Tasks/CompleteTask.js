document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.complete-task-checkbox').forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const taskId = this.getAttribute('data-task-id');
            const form = this.closest('form');
            const actionUrl = form.getAttribute('action');
            
            if (this.checked) {
                Swal.fire({
                    title: 'Êtes-vous sûr ?',
                    text: "Voulez-vous vraiment marquer cette tâche comme terminée ?",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Oui, terminer !',
                    cancelButtonText: 'Annuler'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(actionUrl, { 
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                        }).then(response => {
                            if (response.ok) {
                                document.getElementById(`task-row-${taskId}`).classList.add('text-decoration-line-through');
                                this.disabled = true;
                                Swal.fire(
                                    'Tâche effectuée !',
                                    'La tâche a été marquée comme terminée.',
                                    'success'
                                );
                            } else {
                                this.checked = false;
                                Swal.fire(
                                    'Erreur',
                                    "Erreur lors de la mise à jour de la tâche. Veuillez réessayer.",
                                    'error'
                                );
                            }
                        }).catch(error => {
                            console.error('Error:', error);
                            this.checked = false;
                            Swal.fire(
                                'Erreur',
                                "Erreur lors de la mise à jour de la tâche. Veuillez réessayer.",
                                'error'
                            );
                        });
                    } else {
                        this.checked = false;
                    }
                });
            }
        });
    });
});
