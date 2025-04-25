document.addEventListener('DOMContentLoaded', () => {
    const handleFormSubmit = async (event) => {
        event.preventDefault();

        const form = event.target;
        const teacherId = form.getAttribute('data-teacher-id');
        const formData = new FormData(form);

        const data = {
            teacher_id: teacherId,
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            email: formData.get('email'),
            subject_ids: formData.getAll('subject_ids'),
            session_id: formData.get('session_id'),
            wage: formData.get('wage'),
            wage_system: formData.get('wage_system'),
            currency: formData.get('currency')
        };

        try {
            const response = await fetch(form.action, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    text: result.message
                }).then(() => {
                    window.location.reload();
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    text: result.message
                });
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error!',
            });
        }
    };

    document.querySelectorAll('form[id^="editTeacherForm"]').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

});
