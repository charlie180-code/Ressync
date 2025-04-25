import { showLoadingState, revertToOriginalState } from './StatusHelpers.js';
import validateField from './ValidationHelpers.js';

/**
 * Handles server response by displaying notifications.
 * @param {Response} response - The response from the server.
 * @param {Object} responseData - The data from the server response (parsed JSON).
 */
function handleServerResponse(response, responseData) {
    if (response.ok) {
        Swal.fire({
            title: responseData.title || 'Success',
            text: responseData.message || 'Data saved successfully.',
            icon: 'success',
            confirmButtonText: 'OK'
        });
        window.location.reload();
    } else {
        Swal.fire({
            title: responseData.title || 'Error',
            text: responseData.message || 'Something went wrong.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
}

/**
 * Sends form data to an endpoint, validates fields, updates UI, and handles response.
 * @param {string} formId - The ID of the form to send.
 * @param {string} endpoint - The URL endpoint for the REST API.
 * @param {string} buttonId - The ID of the button to disable/enable during the process.
 * @param {string} spinnerId - The ID of the spinner element to show/hide.
 * @param {string} loadingTextId - The ID of the loading text element to show/hide.
 * @param {Function} validateFn - The validation function that checks the form fields.
 * @param {Object} config - Optional configuration for the API call (e.g., method, headers).
 */
export async function sendDataToAPI(
    formId, 
    endpoint, 
    buttonId, 
    spinnerId, 
    loadingTextId, 
    validateFn, 
    config = {}
) {
    const form = document.getElementById(formId);
    const fields = form.querySelectorAll("[required]");
    let isValid = true;

    fields.forEach(field => {
        const errorText = document.getElementById(field.id + "Error");
        if (!errorText) {
            console.warn(`No error message div found for: ${field.id}`);
        }
        isValid = isValid && validateField(field, errorText, validateFn);
    });

    if (!isValid) {
        return;
    }

    const formData = new FormData(form);

    showLoadingState(buttonId, spinnerId, loadingTextId);

    try {
        const response = await fetch(endpoint, {
            method: config.method || 'POST',
            body: formData,
        });

        const responseData = await response.json();

        handleServerResponse(response, responseData);

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
}
