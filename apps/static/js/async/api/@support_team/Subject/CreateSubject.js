document.querySelector('#createSubjectForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = document.querySelector('#createNewSubjectModal form');
    const name = document.querySelector('#name').value;
    const weight = document.querySelector('#weight').value;
    const teacher = document.querySelector('#teacher').value;
    const classes = [...document.querySelector('#classes').selectedOptions].map(option => option.value);

    const response = await fetch(form.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, weight, teacher, classes })
    });

    const data = await response.json();

    if (response.ok) {
        Swal.fire({
            icon: 'success',
            title: data.title,
            text: data.message
        }).then(() => {
            window.location.reload();
        });
    } else {
        Swal.fire({
            icon: 'error',
            title: data.title,
            text: data.message
        });
    }
});
