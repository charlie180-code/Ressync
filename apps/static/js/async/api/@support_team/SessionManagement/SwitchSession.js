import UtilApiURLs from "../../../../_globals/school/Session.js";

document.addEventListener('DOMContentLoaded', function () {
    const switches = document.querySelectorAll('.form-check-input[type="checkbox"][role="switch"]');

    switches.forEach(function (switchInput) {
        switchInput.addEventListener('change', function () {
            const sessionId = this.dataset.sessionId;
            const isActive = this.checked;

            if (isActive) {
                Swal.fire({
                    title: 'Êtes-vous sûr?',
                    text: "Vous êtes sur le point d'activer cette session.",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Oui, activer!',
                    cancelButtonText: 'Annuler'
                }).then((result) => {
                    if (result.isConfirmed) {
                        updateSessionStatus(sessionId, isActive);
                    } else {
                        switchInput.checked = false;  // Revert the switch if the user cancels
                    }
                });
            } else {
                Swal.fire({
                    title: 'Êtes-vous sûr?',
                    text: "Désactiver cette session entraînera la migration des données vers une nouvelle session.",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Oui, désactiver!',
                    cancelButtonText: 'Annuler'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Open modal for selecting a new session to migrate data
                        const modal = new bootstrap.Modal(document.getElementById('migrateSessionModal'));
                        modal.show();

                        // Add event listener for the modal form submission
                        document.getElementById('migrateSessionForm').addEventListener('submit', function (e) {
                            e.preventDefault();
                            const newSessionId = document.getElementById('newSessionSelect').value;

                            if (newSessionId) {
                                migrateSessionData(sessionId, newSessionId);
                            } else {
                                Swal.fire({
                                    title: 'Erreur',
                                    text: 'Veuillez sélectionner une nouvelle session.',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                });
                            }
                        });
                    } else {
                        switchInput.checked = true;  // Revert the switch if the user cancels
                    }
                });
            }
        });
    });

    function updateSessionStatus(sessionId, isActive) {
        fetch(`${UtilApiURLs.UpdateSessionStatusUrl}${sessionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ active: isActive })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'Session mise à jour',
                    text: 'La session a été bien mise à jour.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({
                    title: 'Erreur',
                    text: 'Une erreur s\'est produite. Veuillez réessayer.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Erreur',
                text: 'Une erreur s\'est produite. Veuillez réessayer.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    }

    function migrateSessionData(sessionId, newSessionId) {
        fetch(`${UtilApiURLs.MigrateSessionData}${sessionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ new_session_id: newSessionId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'Migration réussie',
                    text: 'Les données ont été migrées vers la nouvelle session.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({
                    title: 'Erreur',
                    text: 'Une erreur s\'est produite lors de la migration des données. Veuillez réessayer.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Erreur',
                text: 'Une erreur s\'est produite. Veuillez réessayer.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    }
});
