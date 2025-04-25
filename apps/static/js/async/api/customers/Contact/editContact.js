import domain from "../../../../_globals/domain.js";

document.addEventListener('DOMContentLoaded', function() {
    const editModal = new bootstrap.Modal(document.getElementById('editContactModal'));
    let currentContactId = null;

    document.querySelectorAll('.edit-contact').forEach(button => {
        button.addEventListener('click', function() {
            currentContactId = this.getAttribute('data-contact-id');
            fetchContactData(currentContactId);
        });
    });

    function fetchContactData(contactId) {
        fetch(`${domain}/msg/v1/edit_contact/${contactId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('editFirstName').value = data.first_name || '';
            document.getElementById('editLastName').value = data.last_name || '';
            document.getElementById('editEmail').value = data.email || '';
            document.getElementById('editPhone').value = data.phone || '';
            document.getElementById('editGender').value = data.gender || 'Male';
            
            editModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Failed to load contact data'
            });
        });
    }

    document.getElementById('editContactForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const spinner = document.getElementById('editSpinner');
        const submitBtn = document.getElementById('saveContactChanges');
        
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        const updatedData = {
            first_name: document.getElementById('editFirstName').value,
            last_name: document.getElementById('editLastName').value,
            email: document.getElementById('editEmail').value,
            phone: document.getElementById('editPhone').value,
            gender: document.getElementById('editGender').value
        };

        fetch(`${domain}/msg/v1/edit_contact/${currentContactId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updatedData)
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
                text: 'Failed to update contact'
            });
        })
        .finally(() => {
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        });
    });
});