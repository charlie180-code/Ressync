
const form = document.querySelector('#DeleteStudentForm')
document.addEventListener('DOMContentLoaded', (event) => {
    async function deleteStudent(event) {
        event.preventDefault();

        const button = event.target.closest('.delete-student-button');
        const studentId = button.dataset.studentId;

        const confirmation = await Swal.fire({
            title: 'Êtes-vous sûr?',
            text: "Cette action est irréversible!",
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
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({'student_id':studentId})
                });

                const result = await response.json();

                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: result.title,
                        text: result.message,
                        confirmButtonText: result.confirmButtonText
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: result.title,
                        text: result.message,
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
    }

    // Attach the click event to each delete button
    const deleteButtons = document.querySelectorAll('.delete-student-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', deleteStudent);
    });
});
