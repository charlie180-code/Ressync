import UtilApiURLs from "../../../../../_globals/general/Archive.js";

document.addEventListener('DOMContentLoaded', function () {
    const closeFolderButtons = document.querySelectorAll('.close-folder-button');

    closeFolderButtons.forEach(button => {
        button.addEventListener('click', async function (e) {
            e.preventDefault();
            const folderId = this.getAttribute('data-folder-id');

            if (!folderId) {
                console.error('Folder ID is missing.');
                return;
            }

            const confirmResult = await Swal.fire({
                icon: 'question',
                title: "Fermer le dossier",
                text: "Êtes-vous sûr de vouloir fermer ce dossier?",
                showCancelButton: true,
                confirmButtonText: "Oui",
                cancelButtonText: "Non",
            });

            if (confirmResult.isConfirmed) {
                try {
                    const response = await fetch(`${UtilApiURLs.ChangeFolderStatusURL}/${folderId}/close`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ id: folderId })
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
                            title: "Error!"
                        });
                    }
                } catch (error) {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: "Error!"
                    });
                }
            }
        });
    });
});