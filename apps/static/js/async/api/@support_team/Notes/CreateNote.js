import UtilApiURLs from '../../../../_globals/general/Note.js'

document.addEventListener('DOMContentLoaded', function () {
    const addNoteButton = document.querySelector('#addNoteButton');
    const noteForm = document.querySelector('#noteForm');
    const companyId = noteForm.dataset.companyId

    addNoteButton.addEventListener('click', function (event) {
        event.preventDefault();
        handleFormSubmission();
    });

    function handleFormSubmission() {
        if (!isFormValid()) {
            return;
        }

        disableButton();

        const formData = new FormData(noteForm);

        fetch(noteForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: data.title,
                    text: data.message,
                    icon: 'success',
                    confirmButtonText: data.confirmButtonText
                }).then(() => {
                    window.location.href = `${UtilApiURLs.NoteCreationSuccessURL}/${companyId}`;
                });
            } else {
                showError();
                enableButton();
            }
        })
        .catch(error => {
            showError();
            enableButton();
        });
    }

    function isFormValid() {
        let isValid = true;

        const title = document.querySelector('#NoteTitle');
        const content = document.querySelector('#NoteContent');
        const nature = document.querySelector('#NoteNature');

        if (title.value.trim() === '') {
            document.querySelector('#NoteTitleError').style.display = 'block';
            isValid = false;
        } else {
            document.querySelector('#NoteTitleError').style.display = 'none';
        }

        if (content.value.trim() === '') {
            document.querySelector('#NoteContentError').style.display = 'block';
            isValid = false;
        } else {
            document.querySelector('#NoteContentError').style.display = 'none';
        }

        if (nature.value === '') {
            document.querySelector('#NoteCategoryError').style.display = 'block';
            isValid = false;
        } else {
            document.querySelector('#NoteCategoryError').style.display = 'none';
        }

        return isValid;
    }

    function disableButton() {
        addNoteButton.disabled = true;
        document.querySelector('#PublishText').style.display = 'none';
        document.querySelector('#LoadingText').style.display = 'inline-block';
        document.querySelector('.spinner-border').style.display = 'inline-block';
        document.querySelector('#addNoteButton i').style.display = 'none';
    }

    function enableButton() {
        addNoteButton.disabled = false;
        document.querySelector('#PublishText').style.display = 'inline-block';
        document.querySelector('#LoadingText').style.display = 'none';
        document.querySelector('.spinner-border').style.display = 'none';
        document.querySelector('#addNoteButton i').style.display = 'inline-block';
    }

    function showError(message) {
        Swal.fire({
            title: 'Error!',
            icon: 'error',
        });
    }
});
