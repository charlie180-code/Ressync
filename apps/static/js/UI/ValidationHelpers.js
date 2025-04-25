/**
 * Validates a form field and toggles the visibility of its error message.
 * @param {HTMLElement} field - The form field to validate.
 * @param {HTMLElement} errorText - The associated error text element.
 * @param {Function} validationFn - A callback function that returns `true` if valid, `false` otherwise.
 */
export default function validateField(field, errorText, validationFn) {
    const isValid = validationFn(field.value);

    // Toggle the error message visibility
    errorText.style.display = isValid ? "none" : "block";

    // Optionally, apply error styling to the field
    field.classList.toggle("is-invalid", !isValid);

    return isValid;
}

