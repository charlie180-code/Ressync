import UtilApiURLs from "../../../../_globals/school/UtilsApiUrls.js";

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const adminId = button.dataset.adminId;
            const companyId = button.dataset.companyId;
            const DeleteAdminErrorModal = document.getElementById("DeleteAdminErrorModal");

            Swal.fire({
                title: 'Êtes-vous sûr?',
                text: "Vous ne pourrez pas revenir en arrière!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Oui, supprimer!',
                cancelButtonText: 'Non, annuler!'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const response = await fetch(`${UtilApiURLs.DeleteSchoolAdminUrl}/${companyId}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ user_id: adminId })
                        });

                        if (response.ok) {
                            Swal.fire({
                                icon: 'success',
                                title: 'Administrateur supprimé avec succès!',
                                showConfirmButton: true,
                                confirmButtonText: 'OK'
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    location.reload();
                                }
                            });
                        } else {
                            console.error('Failed to delete admin:', response.statusText);
                            DeleteAdminErrorModal.classList.remove('d-none');
                        }
                    } catch (error) {
                        console.error('Error deleting admin:', error);
                        DeleteAdminErrorModal.classList.remove('d-none');
                    }
                }
            });
        });
    });
});
