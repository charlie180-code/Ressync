document.addEventListener('DOMContentLoaded', function() {
    const createAdminForm = document.getElementById('createAdminForm');
    const createAdminButton = document.getElementById('CreateAdminButton');
    const spinner = document.getElementById('Spinner');
    const buttonText = document.getElementById('ButtonText');

    const nameInput = document.getElementById('adminName');
    const emailInput = document.getElementById('adminEmail');
    const roleInput = document.getElementById('adminRole');

    const firstNameLengthError = document.getElementById('FirstNameLengthError');
    const firstNameEmptyError = document.getElementById('FirstNameEmptyError');
    const emailError = document.getElementById('EmailError');
    const emailEmptyError = document.getElementById('EmailEmptyError');

    function validateName() {
        const name = nameInput.value.trim();
        if (name.length === 0) {
            firstNameEmptyError.classList.remove('d-none');
            firstNameLengthError.classList.add('d-none');
            return false;
        } else if (name.length > 64) {
            firstNameEmptyError.classList.add('d-none');
            firstNameLengthError.classList.remove('d-none');
            return false;
        } else {
            firstNameEmptyError.classList.add('d-none');
            firstNameLengthError.classList.add('d-none');
            return true;
        }
    }

    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (email.length === 0) {
            emailEmptyError.classList.remove('d-none');
            emailError.classList.add('d-none');
            return false;
        } else if (!emailRegex.test(email)) {
            emailEmptyError.classList.add('d-none');
            emailError.classList.remove('d-none');
            return false;
        } else {
            emailEmptyError.classList.add('d-none');
            emailError.classList.add('d-none');
            return true;
        }
    }

    function validateForm() {
        const isNameValid = validateName();
        const isEmailValid = validateEmail();
        return isNameValid && isEmailValid;
    }

    nameInput.addEventListener('input', validateName);
    emailInput.addEventListener('input', validateEmail);

    createAdminButton.addEventListener('click', async function() {
        if (!validateForm()) {
            return;
        }

        createAdminButton.disabled = true;
        spinner.classList.remove('d-none');
        buttonText.classList.add('d-none');

        const formData = new FormData(createAdminForm);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            role_id: formData.get('role_id')
        };

        try {
            const response = await fetch(createAdminForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json()

            if (response.ok) {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'success',
                    confirmButtonText: result.confirmButtonText
                }).then(() => {
                    location.reload();
                });
            } else {
                const errorMessage = await response.text();
                Swal.fire({
                    title: result.title,
                    text: `${errorMessage}`,
                    icon: 'error',
                    confirmButtonText: result.confirmButtonText
                });
            }
        } catch (error) {
            Swal.fire({
                title: 'Error!',
                icon: 'error',
            });
        } finally {
            createAdminButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.classList.remove('d-none');
        }
    });
});
