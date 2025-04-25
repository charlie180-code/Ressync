document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function () {
            const adminId = this.getAttribute('data-admin-id');
            const editButton = document.getElementById(`EditAdminButton${adminId}`);
            
            editButton.addEventListener('click', function () {
                const adminName = document.getElementById(`editAdminName${adminId}`).value;
                const adminEmail = document.getElementById(`editAdminEmail${adminId}`).value;
                const roleId = document.getElementById(`editAdminRole${adminId}`).value;

                if (!adminName || adminName.length > 64) {
                    document.getElementById(`FirstNameLengthError${adminId}`).classList.remove('d-none');
                    return;
                }
                document.getElementById(`FirstNameLengthError${adminId}`).classList.add('d-none');

                if (!adminEmail) {
                    document.getElementById(`EmailEmptyError${adminId}`).classList.remove('d-none');
                    return;
                }
                document.getElementById(`EmailEmptyError${adminId}`).classList.add('d-none');

                editButton.disabled = true;
                document.getElementById(`EditSpinner${adminId}`).classList.remove('d-none');
                document.getElementById(`EditButtonText${adminId}`).classList.add('d-none');

                fetch(window.location.pathname, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: adminId,
                        name: adminName,
                        email: adminEmail,
                        role_id: roleId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    editButton.disabled = false;
                    document.getElementById(`EditSpinner${adminId}`).classList.add('d-none');
                    document.getElementById(`EditButtonText${adminId}`).classList.remove('d-none');

                    Swal.fire({
                        title: data.title,
                        text: data.message || data.error,
                        icon: data.error ? 'error' : 'success',
                        confirmButtonText: data.confirmButtonText
                    }).then(() => {
                        if (!data.error) {
                            location.reload();
                        }
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    editButton.disabled = false;
                    document.getElementById(`EditSpinner${adminId}`).classList.add('d-none');
                    document.getElementById(`EditButtonText${adminId}`).classList.remove('d-none');
                });
            });
        });
    });
});
