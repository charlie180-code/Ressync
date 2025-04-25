document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector('#UpdateStudentGradesTable');
    const gradesTableBody = document.getElementById("gradesTableBody");
    const saveButton = document.getElementById("saveChangesButton");
    const revertButton = document.getElementById("revertChangesButton");
    const spinner = document.getElementById("Spinner");
    const buttonText = document.getElementById("ButtonText");
    const loadingText = document.getElementById("LoadingText");

    let initialTableState = {};

    // Load data from local storage if available
    const savedGrades = JSON.parse(localStorage.getItem('gradesData'));
    if (savedGrades) {
        gradesTableBody.querySelectorAll('tr').forEach((row, index) => {
            const gradeCell = row.querySelector('div[data-grade-id]');
            const studentId = row.getAttribute("data-student-id");
            const savedGrade = savedGrades.find(item => item.student_id === studentId);

            if (savedGrade) {
                gradeCell.innerText = savedGrade.value;
            }

            initialTableState[index] = gradeCell.innerText.trim();
        });
    } else {
        gradesTableBody.querySelectorAll('tr').forEach((row, index) => {
            const gradeCell = row.querySelector('div[data-grade-id]');
            initialTableState[index] = gradeCell.innerText.trim();
        });
    }

    gradesTableBody.addEventListener("input", function() {
        saveButton.style.display = "inline-block";
        revertButton.style.display = "inline-block";
        saveToLocalStorage();
    });

    window.addEventListener('beforeunload', function(e) {
        if (saveButton.style.display === "inline-block") {
            const confirmationMessage = 'Vous avez des changements non enregistrés. Êtes-vous sûr de vouloir quitter?';
            e.returnValue = confirmationMessage;
            return confirmationMessage;
        }
    });

    saveButton.addEventListener("click", async function() {
        saveButton.disabled = true;
        spinner.classList.remove("d-none");
        buttonText.classList.add("d-none");
        loadingText.classList.remove("d-none");

        const rows = gradesTableBody.querySelectorAll("tr");
        const data = [];

        rows.forEach((row) => {
            const gradeCell = row.querySelector("div[data-grade-id]");
            const gradeId = gradeCell.getAttribute("data-grade-id");
            const gradeValue = gradeCell.innerText.trim();

            if (gradeValue !== initialTableState[row.rowIndex - 1]) {
                data.push({
                    id: gradeId || null,
                    value: gradeValue,
                    student_id: row.getAttribute("data-student-id"),
                    subject_id: document.getElementById("subject-select").value,
                    exam_id: document.getElementById("exam-select").value,
                    session_id: document.getElementById("session-select").value
                });
            }
        });

        try {
            const response = await fetch(form.action, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();


            if (response.ok) {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'success',
                    confirmButtonText: result.confirmButtonText
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.reload();
                    }
                });                
                saveButton.style.display = "none";
                revertButton.style.display = "none";
                localStorage.removeItem('gradesData');
            } else {
                Swal.fire({
                    title: result.title,
                    text: result.message,
                    icon: 'error'
                });
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                title: 'Error!',
                icon: 'error'
            });
        } finally {
            saveButton.disabled = false;
            spinner.classList.add("d-none");
            buttonText.classList.remove("d-none");
            loadingText.classList.add("d-none");
        }
    });

    revertButton.addEventListener("click", function() {
        gradesTableBody.querySelectorAll('tr').forEach((row, index) => {
            const gradeCell = row.querySelector('div[data-grade-id]');
            gradeCell.innerText = initialTableState[index];
        });
        saveButton.style.display = "none";
        revertButton.style.display = "none";
        localStorage.removeItem('gradesData');  // Clear local storage after reverting
    });

    function saveToLocalStorage() {
        const rows = gradesTableBody.querySelectorAll("tr");
        const data = [];

        rows.forEach((row) => {
            const gradeCell = row.querySelector("div[data-grade-id]");
            const gradeValue = gradeCell.innerText.trim();

            data.push({
                value: gradeValue,
                student_id: row.getAttribute("data-student-id"),
                subject_id: document.getElementById("subject-select").value,
                exam_id: document.getElementById("exam-select").value,
                session_id: document.getElementById("session-select").value
            });
        });

        localStorage.setItem('gradesData', JSON.stringify(data));
    }
});
