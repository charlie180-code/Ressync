document.querySelector('#UpdateSubjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const updates = [...document.querySelectorAll('input[type="text"]')].map(input => ({
        id: input.name.split('_')[1],
        name: input.value,
        weight: document.querySelector(`#weight_${input.name.split('_')[1]}`).value,
        teachers: [...document.querySelector(`select[name="teachers_${input.name.split('_')[1]}[]"]`).selectedOptions].map(option => option.value),
        classes: [...document.querySelector(`select[name="classes_${input.name.split('_')[1]}[]"]`).selectedOptions].map(option => option.value)
    }));

    for (const update of updates) {
        const response = await fetch(`/manage_subjects/${company_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(update)
        });

        const data = await response.json();

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Succès',
                text: data.message
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: data.message
            });
        }
    }
});
