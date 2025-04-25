import UtilApiURLs from "../../../../_globals/general/Task.js";
const URL = UtilApiURLs.ManageTaskURL;

document.addEventListener('DOMContentLoaded', function () {
    const editButtons = document.querySelectorAll('.edit-task');
    const deleteTaskButtons = document.querySelectorAll('.delete-task');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const taskId = this.dataset.taskId;
            openEditModal(taskId);
        });
    });

    deleteTaskButtons.forEach(button => {
        button.addEventListener('click', function () {
            const taskId = this.dataset.taskId;
            handleTaskDeletion(taskId);
        });
    });

    function openEditModal(taskId) {
        const editTaskForm = document.querySelector(`#editTaskForm${taskId}`);
        const companyId = document.querySelector(`#EditCompanyId${taskId}`).value;
    
        fetch(`${URL}${taskId}/${companyId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success == true) {
                    populateEditForm(data.task, taskId);
                    $(`#EditTaskModal${taskId}`).modal('show');
                } else {
                    showError('Une erreur s\'est produite lors de la récupération des détails de la tâche.');
                }
            })
            .catch(error => {
                console.error('Error fetching task details:', error);
                showError('Une erreur s\'est produite lors de la récupération des détails de la tâche.');
            });
    }
    

    function populateEditForm(task, taskId) {
        document.querySelector(`#EditTaskTitle${taskId}`).value = task.title;
        document.querySelector(`#EditTaskDescription${taskId}`).value = task.description;
        document.querySelector(`#EditAssignedTo${taskId}`).value = task.assigned_to;
        document.querySelector(`#editTaskForm${taskId}`).action = `${URL}${task.id}`;
    }

    document.querySelectorAll('[id^=editTaskButton]').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const taskId = this.dataset.taskId;
            handleFormSubmission(taskId);
        });
    });

    function handleFormSubmission(taskId) {
        const editTaskForm = document.querySelector(`#editTaskForm${taskId}`);
        const companyId = document.querySelector(`#EditCompanyId${taskId}`).value;
    
        if (!isFormValid(taskId)) {
            return;
        }
        
        const formData = {
            title: document.querySelector(`#EditTaskTitle${taskId}`).value,
            description: document.querySelector(`#EditTaskDescription${taskId}`).value,
            assigned_to: document.querySelector(`#EditAssignedTo${taskId}`).value,
            company_id: companyId
        };
    
        fetch(`${URL}${taskId}/${companyId}`, {
            method: 'PUT',
            body: JSON.stringify(formData),
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    title: 'Succès!',
                    text: 'La tâche a été mise à jour avec succès.',
                    icon: 'success',
                    confirmButtonText: 'OK'
                }).then(() => {
                    location.reload();
                });
            } else {
                showError('Une erreur s\'est produite lors de la mise à jour de la tâche.');
            }
        })
        .catch(error => {
            console.error('Error updating task:', error);
            showError('Une erreur s\'est produite lors de la mise à jour de la tâche.');
        });
    }
    

    function isFormValid(taskId) {
        let isValid = true;

        const title = document.querySelector(`#EditTaskTitle${taskId}`);
        const description = document.querySelector(`#EditTaskDescription${taskId}`);
        const assignedTo = document.querySelector(`#EditAssignedTo${taskId}`);

        if (title.value.trim() === '') {
            document.querySelector(`#EditTaskTitleError${taskId}`).style.display = 'block';
            isValid = false;
        } else {
            document.querySelector(`#EditTaskTitleError${taskId}`).style.display = 'none';
        }

        if (description.value.trim() === '') {
            document.querySelector(`#EditTaskDescriptionError${taskId}`).style.display = 'block';
            isValid = false;
        } else {
            document.querySelector(`#EditTaskDescriptionError${taskId}`).style.display = 'none';
        }

        if (assignedTo.value === '0') {
            document.querySelector(`#EditTaskAssignmentError${taskId}`).style.display = 'block';
            isValid = false;
        } else {
            document.querySelector(`#EditTaskAssignmentError${taskId}`).style.display = 'none';
        }

        return isValid;
    }

    function disableButton(taskId) {
        const button = document.querySelector(`#editTaskButton${taskId}`);
        button.disabled = true;
        document.querySelector(`#EditTaskText${taskId}`).style.display = 'none';
        document.querySelector(`#EditLoadingText${taskId}`).style.display = 'inline-block';
        document.querySelector(`.spinner-border${taskId}`).style.display = 'inline-block';
        document.querySelector(`#editTaskButton${taskId} i`).style.display = 'none';
    }

    function enableButton(taskId) {
        const button = document.querySelector(`#editTaskButton${taskId}`);
        button.disabled = false;
        document.querySelector(`#EditTaskText${taskId}`).style.display = 'inline-block';
        document.querySelector(`#EditLoadingText${taskId}`).style.display = 'none';
        document.querySelector(`.spinner-border${taskId}`).style.display = 'none';
        document.querySelector(`#editTaskButton${taskId}`).style.display = 'inline-block';
    }

    function showError(message) {
        Swal.fire({
            title: 'Erreur!',
            text: message,
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
});
