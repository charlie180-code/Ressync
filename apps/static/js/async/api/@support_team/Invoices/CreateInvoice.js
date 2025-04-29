document.addEventListener('DOMContentLoaded', () => {
    const attachCheckbox = document.getElementById('attachToProject');
    const projectSelect = document.getElementById('projectSelect');
    
    attachCheckbox.addEventListener('change', () => {
        projectSelect.disabled = !attachCheckbox.checked;
        if (!attachCheckbox.checked) {
            projectSelect.value = '';
        }
    });

    document.getElementById('clientCountry').addEventListener('change', function() {
        const country = this.value;
        const currencySelect = document.getElementById('preferredCurrency');
        
        if (country === 'Niger') {
            currencySelect.value = 'XOF';
        } else if (country === 'France' || country === 'Germany') {
            currencySelect.value = 'EUR';
        }
    });

    const form = document.getElementById('createInvoiceForm');
    const submitButton = document.getElementById('submitButton');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('buttonText');
    const loadingText = document.getElementById('loadingText');

    submitButton.addEventListener('click', async (event) => {
        event.preventDefault();

        const formData = new FormData(form);
        const jsonData = {};

        if (attachCheckbox.checked && !projectSelect.value) {
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: 'Please select a project to attach the invoice to'
            });
            return;
        }

        formData.forEach((value, key) => {
            const keys = key.split('[').map(k => k.replace(']', ''));
            let obj = jsonData;

            for (let i = 0; i < keys.length - 1; i++) {
                if (!obj[keys[i]]) obj[keys[i]] = {};
                obj = obj[keys[i]];
            }
            obj[keys[keys.length - 1]] = value;
        });

        submitButton.disabled = true;
        spinner.classList.remove('d-none');
        buttonText.classList.add('d-none');
        loadingText.classList.remove('d-none');

        try {
            const response = await fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData)
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/pdf')) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'invoice.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                
            } else {
                const result = await response.json();
                if (result.success) {
                    Swal.fire({
                        icon: 'success',
                        title: result.title,
                        text: result.message,
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: result.message
                    });
                }
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: error.message
            });
        } finally {
            submitButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.classList.remove('d-none');
            loadingText.classList.add('d-none');
        }
    });
});