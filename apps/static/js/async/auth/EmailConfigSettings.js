/**
 * Email Configuration Handler
 * Handles the email provider selection, password visibility toggle,
 * and connection testing functionality.
 */

import domain from '../../_globals/domain.js'

document.addEventListener('DOMContentLoaded', function() {
    const emailProviderDropdown = document.getElementById('EmailProviderDropdown');
    const providerLogo = document.getElementById('providerLogo');
    const providerName = document.getElementById('providerName');
    const emailProviderInput = document.getElementById('EmailProviderInput');
    const customServerFields = document.getElementById('customServerFields');
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const toggleEmailPasswordBtn = document.getElementById('toggleEmailPassword');
    const eyeIconEmail = document.getElementById('eyeIconEmail');
    const emailPasswordInput = document.getElementById('EmailPassword');
    const testConnectionBtn = document.getElementById('testEmailConnection');
    const testConnectionSpinner = document.getElementById('testConnectionSpinner');
    const testConnectionResult = document.getElementById('testConnectionResult');

    function initializeProvider() {
        const currentProvider = emailProviderInput.value;
        if (currentProvider) {
            const currentItem = Array.from(dropdownItems).find(item => 
                item.getAttribute('data-value') === currentProvider);
            if (currentItem) {
                providerLogo.src = currentItem.getAttribute('data-logo');
                providerLogo.style.display = 'inline';
                providerName.textContent = currentItem.textContent.trim();
            }
        }
        toggleCustomFields(currentProvider);
    }

    function toggleCustomFields(provider) {
        customServerFields.style.display = provider === 'custom' ? 'block' : 'none';
    }

    function setupProviderSelection() {
        dropdownItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedValue = this.getAttribute('data-value');
                const selectedLogo = this.getAttribute('data-logo');
                const selectedText = this.textContent.trim();
                
                providerName.textContent = selectedText;
                emailProviderInput.value = selectedValue;
                providerLogo.src = selectedLogo;
                providerLogo.style.display = 'inline';
                
                toggleCustomFields(selectedValue);
            });
        });
    }

    function setupPasswordToggle() {
        toggleEmailPasswordBtn.addEventListener('click', function() {
            if (emailPasswordInput.type === "password") {
                emailPasswordInput.type = "text";
                eyeIconEmail.setAttribute("fill", "green");
            } else {
                emailPasswordInput.type = "password";
                eyeIconEmail.setAttribute("fill", "gray"); 
            }
        });
    }

    function setupConnectionTest() {
        testConnectionBtn.addEventListener('click', function() {
            const emailProvider = emailProviderInput.value;
            const emailUsername = document.getElementById('EmailUsername').value;
            const emailPassword = emailPasswordInput.value;
            const smtpServer = document.querySelector('input[name="smtp_server"]')?.value;
            const smtpPort = document.querySelector('input[name="smtp_port"]')?.value;
            
            if (!emailUsername || !emailPassword) {
                showTestResult("Please provide an email and password", false);
                return;
            }
            
            testConnectionSpinner.classList.remove('d-none');
            testConnectionBtn.disabled = true;
            testConnectionResult.textContent = '';
            
            const formData = new FormData();
            formData.append('email_provider', emailProvider);
            formData.append('email_username', emailUsername);
            formData.append('email_password', emailPassword);
            if (emailProvider === 'custom') {
                formData.append('smtp_server', smtpServer);
                formData.append('smtp_port', smtpPort);
            }
            
            fetch(`${domain}/msg/v1/test_email_connection`, {
                method: 'POST',
                body: formData
            })
            .then(handleTestResponse)
            .catch(handleTestError)
            .finally(resetTestButton);
        });
    }

    function handleTestResponse(response) {
        return response.json().then(data => {
            if (data.success) {
                showTestResult("Connexion successful!", true);
            } else {
                showTestResult(data.message, false);
            }
        });
    }

    function handleTestError(error) {
        showTestResult("Error while testing", false);
        console.error('Connection test error:', error);
    }

    function resetTestButton() {
        testConnectionSpinner.classList.add('d-none');
        testConnectionBtn.disabled = false;
    }

    function showTestResult(message, isSuccess) {
        testConnectionResult.textContent = message;
        testConnectionResult.style.color = isSuccess ? 'green' : 'red';
    }

    function init() {
        initializeProvider();
        setupProviderSelection();
        setupPasswordToggle();
        setupConnectionTest();
    }

    init();
});