/**
 * Toggles spinner visibility and content state for any form or UI element.
 * @param {string} buttonId - The ID of the submit button to disable/enable.
 * @param {string} spinnerId - The ID of the spinner element to show/hide.
 * @param {string} loadingTextId - The ID of the loading text element to show/hide.
 */
export function showLoadingState(buttonId, spinnerId, loadingTextId) {
    const button = document.getElementById(buttonId);
    const spinner = document.getElementById(spinnerId);
    const loadingText = document.getElementById(loadingTextId);

    button.disabled = true;

    button.querySelector('i').classList.add('d-none');
    button.querySelector('span').classList.add('d-none');
    spinner.classList.remove('d-none');
    loadingText.classList.remove('d-none');
}

/**
 * Reverts the submit button to its original state after the loading process.
 * @param {string} buttonId - The ID of the submit button to enable/restore.
 * @param {string} spinnerId - The ID of the spinner element to hide.
 * @param {string} loadingTextId - The ID of the loading text element to hide.
 */
export function revertToOriginalState(buttonId, spinnerId, loadingTextId) {
    const button = document.getElementById(buttonId);
    const spinner = document.getElementById(spinnerId);
    const loadingText = document.getElementById(loadingTextId);

    button.disabled = false;

    button.querySelector('i').classList.remove('d-none');
    button.querySelector('span').classList.remove('d-none');
    spinner.classList.add('d-none');
    loadingText.classList.add('d-none');
}
