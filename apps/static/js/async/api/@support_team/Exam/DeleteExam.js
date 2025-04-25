const form = document.querySelector('#DeleteExamForm')

document.addEventListener('DOMContentLoaded', function() {
    const deleteExamButtons = document.querySelectorAll('.delete-exam-btn');

    deleteExamButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const examId = this.getAttribute('data-exam-id');

            const confirmation = await Swal.fire({
                title: 'Êtes-vous sûr?',
                text: 'Voulez-vous vraiment supprimer cet examen?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Oui, supprimer!',
                cancelButtonText: 'Annuler'
            });

            if (confirmation.isConfirmed) {
                try {
                    const response = await fetch(form.action, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body : JSON.stringify({'examId':examId})
                    });

                    const result = await response.json();

                    if (response.ok) {
                        Swal.fire({
                            icon: 'success',
                            text: result.message,
                            confirmButtonText: result.confirmButtonText
                        }).then(() => {
                            location.reload();
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            text: result.error,
                            confirmButtonText: result.confirmButtonText
                        });
                    }
                } catch (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                    });
                }
            }
        });
    });
});
