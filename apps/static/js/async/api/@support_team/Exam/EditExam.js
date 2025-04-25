document.addEventListener('DOMContentLoaded', function() {
    const editExamForms = document.querySelectorAll('.edit-exam-form');

    editExamForms.forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            const examId = this.getAttribute('data-exam-id');
            const formData = new FormData(this);
            const data = {
                examType: formData.get('examType'),
                examDate: formData.get('examDate'),
                examSubject: formData.get('examSubject'),
                examClass: formData.get('examClass'),
                examSession: formData.get('examSession'),
                examGradeValue: formData.get('examGradeValue'),
                examId:examId
            };


            try {
                const response = await fetch(this.action, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
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
        });
    });
});
