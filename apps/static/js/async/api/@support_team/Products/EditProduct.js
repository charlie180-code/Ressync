import UtilApiURLs from "../../../../_globals/UtilApiUrls.js";

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('editProductBtn').addEventListener('click', function () {
        var productId = document.getElementById('productId').value;
        var formData = new FormData(document.getElementById('editProductForm'));
        formData.append('id', productId);

        fetch(UtilApiURLs.ManageProductURL, {
            method: 'PUT',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            Swal.fire({
                icon: 'success',
                title: data.title,
                text: data.message,
                confirmButtonText: data.confirmButtonText,
            }).then(function () {
                location.reload();
            });
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                showConfirmButton: false,
                timer: 1500
            });
        });
    });
});