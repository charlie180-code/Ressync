document.addEventListener('DOMContentLoaded', function () {
    const createFolderForm = document.getElementById('createFolderForm');
    const CreateFolderButtonText = document.getElementById('CreateFolderButtonText');
    const loadingText = document.getElementById('CreateFolderLoadingText');
    const CreateFolderSubmitButton = document.getElementById('CreateFolderSubmitButton')

    createFolderForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        loadingText.style.display = 'block';
        CreateFolderButtonText.style.display = 'none';
        CreateFolderSubmitButton.disabled = true

        const formData = new FormData(createFolderForm);
        const data = {
            folder_name: formData.get('name'),
            folder_description: formData.get('description'),
            folder_type: formData.get('discipline'),
            client: formData.get('client'),
            deadline: formData.get('deadline'),
            ...extractAdditionalFields(formData)
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
            loadingText.style.display = 'none';
            CreateFolderButtonText.style.display = 'block';
            CreateFolderSubmitButton.disabled = false
        }
    });

    function extractAdditionalFields(formData) {
        let additionalFields = {};
        const discipline = formData.get('discipline');

        if (discipline === 'Electricité') {
            additionalFields = {
                voltage: formData.get('voltage'),
                current: formData.get('current'),
                compliance_standards: formData.get('compliance_standards'),
            };
        } else if (discipline === 'Electronique') {
            additionalFields = {
                circuit_type: formData.get('circuit_type'),
                power_rating: formData.get('power_rating'),
                components_list: formData.get('components_list'),
                firmware_version: formData.get('firmware_version'),
            };
        } else if (discipline === 'Génie civil') {
            additionalFields = {
                project_location: formData.get('project_location'),
                project_manager: formData.get('project_manager'),
                project_phase: formData.get('project_phase'),
                budget: formData.get('budget'),
                contractor: formData.get('contractor'),
                materials_used: formData.get('materials_used'),
                permits_approved: formData.get('permits_approved') === 'on',
            };
        } else if (discipline === 'Biomédical') {
            additionalFields = {
                equipment_type: formData.get('equipment_type'),
                safety_standards: formData.get('safety_standards'),
            };
        }

        return additionalFields;
    }
});
