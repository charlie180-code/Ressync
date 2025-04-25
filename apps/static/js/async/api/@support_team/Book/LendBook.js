document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.Lendbookforms').forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            
            let formData = new FormData(this);
            let submitButton = this.querySelector('button[type="submit"]');
            let spinner = submitButton.querySelector('#spinner');
            let buttonText = submitButton.querySelector('#ButtonText');
            
            // Show spinner and disable button
            spinner.classList.remove('d-none');
            buttonText.classList.add('d-none');
            submitButton.disabled = true;

            fetch(this.action, {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                // Hide spinner and enable button
                spinner.classList.add('d-none');
                buttonText.classList.remove('d-none');
                submitButton.disabled = false;

                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: data.title,
                        text: data.message,
                    }).then(() => {
                        location.reload();  // Reload the page or update the UI
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: data.title,
                        text: data.message,
                    });
                }
            })
            .catch(error => {
                // Hide spinner and enable button
                spinner.classList.add('d-none');
                buttonText.classList.remove('d-none');
                submitButton.disabled = false;

                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                });
            });
        });
    });
});
