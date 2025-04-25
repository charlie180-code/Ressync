import UtilApiURLs from "../../../../_globals/general/Note.js";
const URL = UtilApiURLs.ManageNoteURL;

document.addEventListener('DOMContentLoaded', function () {
    const deleteNoteButtons = document.querySelectorAll('.delete-note');

    deleteNoteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const noteId = this.dataset.noteId;
            handleNoteDeletion(noteId);
        });
    });

    function handleNoteDeletion(noteId) {
        Swal.fire({
            title: 'Êtes-vous sûr ?',
            text: 'Vous ne pourrez pas récupérer cette note !',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Supprimer',
            cancelButtonText: 'Annuler',
            dangerMode: true,
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`${URL}${noteId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire(data.title, data.message, 'success')
                            .then(() => location.reload());
                    } else {
                        Swal.fire('Error!', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error deleting note:', error);
                    Swal.fire('Error!', 'error');
                });
            }
        });
    }
});
