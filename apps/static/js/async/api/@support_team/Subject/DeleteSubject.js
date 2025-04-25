const deleteForms = document.querySelectorAll('#DeleteSubjectForm');

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-subject-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const subjectId = button.dataset.subjectId;

            try {
                const result = await Swal.fire({
                    title: 'Êtes-vous sûr?',
                    text: "Cette action est irréversible!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Oui, supprimer!',
                    cancelButtonText: 'Annuler'
                });

                if (result.isConfirmed) {
                    // Find the corresponding form for the clicked button
                    const form = Array.from(deleteForms).find(form => form.querySelector('.delete-subject-btn[data-subject-id="' + subjectId + '"]'));

                    const response = await fetch(form.action, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            id: subjectId,
                        }),
                    });

                    const data = await response.json();

                    if (response.ok) {
                        Swal.fire({
                            icon: 'success',
                            title: data.title,
                            text: data.message,
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: data.title,
                            text: data.message,
                        });
                    }
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                });
            }
        });
    });
});
