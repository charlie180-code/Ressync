import UtilApiURLs from "../../../../_globals/shipping/Store.js";

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#createAdForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            Swal.fire({
                icon: 'success',
                title: data.title,
                text: data.message,
                confirmButtonText: data.confirmButtonText
            }).then((result) => {
                if (result.isConfirmed) {
                    location.reload();
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error!'
            });
        });
    });
});
