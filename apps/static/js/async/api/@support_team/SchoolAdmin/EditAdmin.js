document.addEventListener('DOMContentLoaded', function() {
    const editAdminForms = document.querySelectorAll('form[id^="editAdminForm"]');

    editAdminForms.forEach(function(editAdminForm) {
        const adminId = editAdminForm.dataset.adminId;
        const editAdminButton = document.getElementById(`EditAdminButton${adminId}`);
        const spinner = document.getElementById(`EditSpinner${adminId}`);
        const buttonText = document.getElementById(`EditButtonText${adminId}`);

        const nameInput = document.getElementById(`editAdminName${adminId}`);
        const emailInput = document.getElementById(`editAdminEmail${adminId}`);
        const roleInput = document.getElementById(`editAdminRole${adminId}`);

        const firstNameEmptyError = document.getElementById(`FirstNameEmptyError${adminId}`);
        const firstNameLengthError = document.getElementById(`FirstNameLengthError${adminId}`);
        const emailEmptyError = document.getElementById(`EmailEmptyError${adminId}`);
        const emailError = document.getElementById(`EmailError${adminId}`);

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

        editAdminButton.addEventListener('click', async function() {
            if (!validateForm()) {
                return;
            }

            editAdminButton.disabled = true;
            spinner.classList.remove('d-none');
            buttonText.classList.add('d-none');

            const formData = new FormData(editAdminForm);
            const data = {
                user_id: adminId,
                name: formData.get('name'),
                email: formData.get('email'),
                role_id: formData.get('role_id')
            };

            try {
                const response = await fetch(editAdminForm.action, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json()

                if (response.ok) {
                    Swal.fire({
                        icon: 'success',
                        title: result.title,
                        showConfirmButton: result.showConfirmButton,
                        confirmButtonText: result.confirmButtonText
                    }).then((result) => {
                        if (result.isConfirmed) {
                            location.reload();
                        }
                    });
                } else {
                    console.error('Failed to update admin');
                    Swal.fire({
                        title: result.title,
                        text: result.message,
                        icon: 'error',
                        confirmButtonText: result.confirmButtonText
                    });
                }
            } catch (error) {
                console.error('Error updating admin:', error);
                Swal.fire({
                    title: 'Error!',
                    icon: 'error',
                });
            } finally {
                editAdminButton.disabled = false;
                spinner.classList.add('d-none');
                buttonText.classList.remove('d-none');
            }
        });
    });
});
