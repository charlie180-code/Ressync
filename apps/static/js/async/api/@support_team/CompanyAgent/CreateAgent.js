document.addEventListener('DOMContentLoaded', function () {
    const createAdminButton = document.getElementById('CreateAdminButton');

    createAdminButton.addEventListener('click', function () {
        const adminName = document.getElementById('NewAgentName').value;
        const adminEmail = document.getElementById('NewAgentEmail').value;
        const roleName = document.getElementById('NewAgentRole').value;
        const position = document.getElementById('NewAgentposition').value;
        const roleId = document.querySelector(`#roleNames option[value="${roleName}"]`).getAttribute('data-role-id');
        
        const StationElement = document.getElementById("NewAgentStation")
        const station = null
        
        if(StationElement){
            const station = document.getElementById("NewAgentStation").value;
        }


        if (!adminName || adminName.length > 64) {
            document.getElementById('FirstNameLengthError').classList.remove('d-none');
            return; 
        }
        document.getElementById('FirstNameLengthError').classList.add('d-none');

        if (!adminEmail) {
            document.getElementById('EmailEmptyError').classList.remove('d-none');
            return;
        }
        document.getElementById('EmailEmptyError').classList.add('d-none');

        createAdminButton.disabled = true;
        document.getElementById('Spinner').classList.remove('d-none');
        document.getElementById('ButtonText').classList.add('d-none');

        fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: adminName,
                email: adminEmail,
                role_id: roleId,
                position: position,
                station: station
            })
        })
        .then(response => response.json())
        .then(data => {
            createAdminButton.disabled = false;
            document.getElementById('Spinner').classList.add('d-none');
            document.getElementById('ButtonText').classList.remove('d-none');

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
            createAdminButton.disabled = false;
            document.getElementById('Spinner').classList.add('d-none');
            document.getElementById('ButtonText').classList.remove('d-none');
        });
    });
});
