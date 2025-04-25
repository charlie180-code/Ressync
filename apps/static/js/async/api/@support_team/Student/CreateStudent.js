function generateRandomString(length = 6) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars[Math.floor(Math.random() * chars.length)];
    }
    return result;
}

function generateEmail(firstName, lastName) {
    const domain = "example.com";
    const randomString = generateRandomString();
    return `${firstName.toLowerCase()}.${lastName.toLowerCase()}.${randomString}@${domain}`;
}

function updateEmails() {
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;

    if (firstName && lastName) {
        const studentEmail = generateEmail(firstName, lastName);
        document.getElementById('email').value = studentEmail;

        const parentFirstName = document.getElementById('parentFirstName').value || `${firstName}_parent`;
        const parentLastName = document.getElementById('parentLastName').value || lastName;
        const parentEmail = generateEmail(parentFirstName, parentLastName);
        document.getElementById('parentEmail').value = parentEmail;
    }
}

document.getElementById('firstName').addEventListener('input', updateEmails);
document.getElementById('lastName').addEventListener('input', updateEmails);

document.getElementById('createStudentForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const submitButton = document.getElementById('CreateStudentButton');
    submitButton.disabled = true;

    document.getElementById('spinner').classList.remove('d-none');
    document.getElementById('ButtonText').classList.add('d-none');
    document.getElementById('LoadingText').classList.remove('d-none');

    const formData = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        gender: document.getElementById('gender').value,
        dateOfBirth: document.getElementById('dateOfBirth').value,
        placeOfBirth: document.getElementById('placeOfBirth').value,
        classId: document.getElementById('classId').value,
        sessionId: document.getElementById('sessionId').value,
        email: document.getElementById('email').value,
        parentFirstName: document.getElementById('parentFirstName').value,
        parentLastName: document.getElementById('parentLastName').value,
        parentEmail: document.getElementById('parentEmail').value,
        firstInstallment: document.getElementById('firstInstallment').value,
        currency: document.getElementById('currency').value
    };

    try {
        const response = await fetch(e.target.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const blob = await response.blob(); // Get the response as a Blob (PDF file)
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'invoice.pdf'; // Set the default name for the PDF file
            document.body.appendChild(a);
            a.click();
            a.remove();

            Swal.fire({
                title: 'Ajouté',
                text: 'L\'élève a été ajouté avec succès!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => location.reload());
        } else {
            const result = await response.json();
            Swal.fire({
                title: 'Erreur',
                text: result.error,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    } catch (error) {
        Swal.fire({
            text: error.message,
            icon: 'error',
            confirmButtonText: error.confirmButtonText
        });
    } finally {
        submitButton.disabled = false;
        document.getElementById('spinner').classList.add('d-none');
        document.getElementById('ButtonText').classList.remove('d-none');
        document.getElementById('LoadingText').classList.add('d-none');
    }
});
