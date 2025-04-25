document.addEventListener('DOMContentLoaded', function() {
    const createExamForm = document.getElementById('createExamForm');

    createExamForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData(createExamForm);
        const data = {
            examName: formData.get('examName'),
            examType: formData.get('examType'),
            examDate: formData.get('examDate'),
            examSubject: formData.get('examSubject'),
            examClass: formData.get('examClass'),
            examSession: formData.get('examSession'),
            examGradeValue: formData.get('examGradeValue')
        };
        console.log(formData)

        try {
            const response = await fetch(createExamForm.action, {
                method: 'POST',
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
