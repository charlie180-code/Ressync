import { showLoadingState, revertToOriginalState } from '../../../../UI/StatusHelpers.js';
import validateField from '../../../../UI/ValidationHelpers.js';
import domain from '../../../../_globals/domain.js';

document.getElementById('createLetterForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const form = this;
    const buttonId = 'SubmitButton';
    const spinnerId = 'Spinner';
    const loadingTextId = 'ButtonText';
    const endpoint = `${domain}/order/v1/create_new_container_release_letter`;
    
    showLoadingState(buttonId, spinnerId, loadingTextId);
    
    try {
        const fields = form.querySelectorAll("[required]");
        let isValid = true;
        
        fields.forEach(field => {
            const errorText = document.getElementById(field.id + "Error");
            if (errorText) {
                isValid = isValid && validateField(field, errorText, (value) => value.trim() !== '');
            }
        });
        
        const emailFields = form.querySelectorAll("input[type='email']");
        emailFields.forEach(field => {
            const errorText = document.getElementById(field.id + "Error");
            if (errorText && field.value.trim() !== '') {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                isValid = isValid && validateField(field, errorText, (value) => emailRegex.test(value));
            }
        });
        
        if (!isValid) {
            revertToOriginalState(buttonId, spinnerId, loadingTextId);
            return;
        }
        
        const formData = new FormData(form);
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const jsonData = response.headers.get('X-JSON-Data');
            const responseData = jsonData ? JSON.parse(jsonData) : {};
            
            Swal.fire({
                title: responseData.title || 'Success',
                text: responseData.message || 'Data saved successfully.',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                response.blob().then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = responseData.pdf_filename || 'document.pdf';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    a.remove();
                    
                    window.location.reload();
                });
            });
        } else {
            const errorData = await response.json();
            Swal.fire({
                title: errorData.title || 'Error',
                text: errorData.message || 'Something went wrong.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    } catch (error) {
        Swal.fire({
            title: 'Network Error!',
            text: 'Please try again later.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    } finally {
        revertToOriginalState(buttonId, spinnerId, loadingTextId);
    }
});