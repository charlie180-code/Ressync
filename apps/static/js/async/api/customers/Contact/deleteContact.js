import domain from "../../../../_globals/domain.js";

document.addEventListener('DOMContentLoaded', function() {
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteContactModal'));
    let currentContactId = null;

    document.querySelectorAll('.delete-contact').forEach(button => {
        button.addEventListener('click', function() {
            currentContactId = this.getAttribute('data-contact-id');
            deleteModal.show();
        });
    });

    document.getElementById('confirmDeleteContact').addEventListener('click', function() {
        const spinner = document.getElementById('deleteSpinner');
        const deleteBtn = document.getElementById('confirmDeleteContact');
        
        spinner.classList.remove('d-none');
        deleteBtn.disabled = true;

        fetch(`${domain}/msg/v1/delete_contact/${currentContactId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: data.title,
                    text: data.message
                }).then(() => {
                    window.location.reload();
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Failed to delete contact'
            });
        })
        .finally(() => {
            spinner.classList.add('d-none');
            deleteBtn.disabled = false;
            deleteModal.hide();
        });
    });
});