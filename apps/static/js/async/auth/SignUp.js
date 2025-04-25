import UtilApiURLs from "../../_globals/general/Auth.js";

document.addEventListener('DOMContentLoaded', () => {
    const personalForm = document.getElementById('personalForm');
    const submitButton = document.getElementById('submitButton');
    const spinner = document.getElementById('Spinner');
    const buttonText = document.getElementById('button-text');

    const errorMessages = personalForm.querySelectorAll('.error-message');
    const emailErrorMessage = document.getElementById('emailError');
    const invalidEmailErrorMessage = document.getElementById('invalidEmailErrorMessage');
    const passwordErrorMessage = document.getElementById('passwordError');
    const confirmPasswordErrorMessage = document.getElementById('confirmPasswordError');
    const toolsErrorMessage = document.getElementById('toolsError');

    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');

    errorMessages.forEach(msg => msg.classList.add('hidden'));

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const validateForm = () => {
        let isValid = true;
    
        errorMessages.forEach(msg => msg.classList.add('hidden'));
        emailInput.classList.remove('border-red-500');
        passwordInput.classList.remove('border-red-500');
        confirmPasswordInput.classList.remove('border-red-500');
    
        if (!emailInput.value) {
            emailInput.classList.add('border-red-500');
            emailErrorMessage.classList.remove('hidden');
            isValid = false;
        } else if (!validateEmail(emailInput.value)) {
            emailInput.classList.add('border-red-500');
            invalidEmailErrorMessage.classList.remove('hidden');
            isValid = false;
        }
    
        if (passwordInput.value.length < 8) {
            passwordInput.classList.add('border-red-500');
            passwordErrorMessage.classList.remove('hidden');
            isValid = false;
        }
    
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.classList.add('border-red-500');
            confirmPasswordErrorMessage.classList.remove('hidden');
            isValid = false;
        }
    
        const selectedTools = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'));
        if (selectedTools.length === 0) {
            toolsErrorMessage.classList.remove('hidden');
            isValid = false;
        } else {
            toolsErrorMessage.classList.add('hidden');
        }
    
        submitButton.disabled = !isValid;
    
        return isValid;
    };
    

    [emailInput, passwordInput, confirmPasswordInput].forEach(input => {
        input.addEventListener('input', validateForm);
    });
    
    const toolCheckboxes = document.querySelectorAll('input[type="checkbox"]');
    toolCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', validateForm);
    });

    submitButton.addEventListener('click', async () => {
        if (!validateForm()) {
            return;
        }

        spinner.classList.remove('hidden');
        buttonText.textContent = "En cours...";

        const formData = {
            firstName: document.getElementById('firstName').value,
            lastName: document.getElementById('lastName').value,
            email: emailInput.value,
            password: passwordInput.value,
            confirmPassword: confirmPasswordInput.value,
            tools: Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value),
            field: document.getElementById('field').value,
        };

        try {
            const response = await fetch(UtilApiURLs.SignupNewUser, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();

            if (result.success) {
                window.location.href = UtilApiURLs.CompanyCreationSuccessURL;
            } else {
                emailInput.classList.remove('border-red-500');
                passwordInput.classList.remove('border-red-500');
                confirmPasswordInput.classList.remove('border-red-500');
                errorMessages.forEach(msg => msg.classList.add('hidden'));

                if (result.message === 'email_exists') {
                    emailInput.classList.add('border-red-500');
                    emailErrorMessage.classList.remove('hidden');
                } else if (result.message === 'password_mismatch') {
                    confirmPasswordInput.classList.add('border-red-500');
                    confirmPasswordErrorMessage.classList.remove('hidden');
                } else if (result.message === 'weak_password') {
                    passwordInput.classList.add('border-red-500');
                    passwordErrorMessage.classList.remove('hidden');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Une erreur s\'est produite. Veuillez réessayer.');
        } finally {
            spinner.classList.add('hidden');
            buttonText.textContent = "Continuer";
        }
    });
});
