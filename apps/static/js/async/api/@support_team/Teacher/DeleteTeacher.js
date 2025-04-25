const form = document.querySelector('#DeleteTeacherForm')

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(button => {
        button.addEventListener('click', () => {
            const deleteButton = button.closest('tr').querySelector('.delete-teacher-btn');
            if (deleteButton) {
                deleteButton.addEventListener('click', async () => {
                    const teacherId = deleteButton.dataset.teacherId;
                    try {
                        const response = await fetch(form.action, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({'teacher_id':teacherId})
                        });
                        
                        if (response.ok) {
                            const result = await response.json();
                            Swal.fire({
                                icon: 'success',
                                text: result.message,
                                confirmButtonText: result.confirmButtonText
                            }).then(() => {
                                window.location.reload();
                            });
                        } else {
                            const result = await response.json();
                            Swal.fire({
                                icon: 'error',
                                text: result.message
                            });
                        }
                    } catch (error) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error!',
                        });
                    }
                });
            }
        });
    });
});
