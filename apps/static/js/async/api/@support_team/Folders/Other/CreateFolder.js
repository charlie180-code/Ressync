document.addEventListener('DOMContentLoaded', function () {
    const createFolderForm = document.getElementById('createFolderForm');
    const CreateFolderButtonText = document.getElementById('CreateFolderButtonText')
    const loadingText = document.getElementById('CreateFolderLoadingText');
    const CreateFolderSubmitButton = document.getElementById('CreateFolderSubmitButton')


    createFolderForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        CreateFolderButtonText.style.display = 'none';
        loadingText.style.display = 'block';
        CreateFolderSubmitButton.disabled = true

        const formData = new FormData(createFolderForm);
        const data = {
            folder_name: formData.get('name'),
            folder_description: formData.get('description'),
            client: formData.get('client'),
            folder_type: formData.get('type'),
            transport: formData.get('transport'),
            weight: formData.get('weight'),
            bills_of_ladding: formData.get('bills_of_ladding'),
            deadline: formData.get('deadline')
        };

        try {
            const response = await fetch(createFolderForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: result.title,
                    text: result.message,
                    confirmButtonText: result.confirmButtonText
                }).then(() => {
                    window.location.reload();
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: result.message,
                });
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error!',
            });
        } finally {
            CreateFolderButtonText.style.display = 'block'
            loadingText.style.display = 'none';
            CreateFolderSubmitButton.disabled = false
        }
    });
});
