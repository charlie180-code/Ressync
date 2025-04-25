document.addEventListener("DOMContentLoaded", function() {
    const attendanceForm = document.querySelector('#UpdateAttendanceForm');
    const attendanceTableBody = attendanceForm.querySelector('tbody');
    const saveButton = document.getElementById("saveChangesButton");
    const revertButton = document.getElementById("revertChangesButton");
    const spinner = document.getElementById("Spinner");
    const buttonText = document.getElementById("ButtonText");
    const loadingText = document.getElementById("LoadingText");

    let initialTableState = {};

    // Load data from local storage if available
    const savedAttendance = JSON.parse(localStorage.getItem('attendanceData'));
    if (savedAttendance) {
        attendanceTableBody.querySelectorAll('tr[data-student-id]').forEach((row, index) => {
            const attendanceTypeCell = row.querySelector('.attendance-type');
            const attendanceNumberCell = row.querySelector('.attendance-number');
            const studentId = row.getAttribute("data-student-id");

            const savedEntry = savedAttendance.find(item => item.student_id === studentId);
            if (savedEntry) {
                attendanceTypeCell.value = savedEntry.type;
                attendanceNumberCell.value = savedEntry.number;
            }

            initialTableState[index] = {
                type: attendanceTypeCell.value,
                number: attendanceNumberCell.value
            };
        });
    } else {
        attendanceTableBody.querySelectorAll('tr[data-student-id]').forEach((row, index) => {
            const attendanceTypeCell = row.querySelector('.attendance-type');
            const attendanceNumberCell = row.querySelector('.attendance-number');

            initialTableState[index] = {
                type: attendanceTypeCell.value,
                number: attendanceNumberCell.value
            };
        });
    }

    attendanceTableBody.addEventListener("input", function() {
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

    saveButton.addEventListener("click", async function(e) {
        e.preventDefault();
        saveButton.disabled = true;
        spinner.classList.remove("d-none");
        buttonText.classList.add("d-none");
        loadingText.classList.remove("d-none");

        const rows = attendanceTableBody.querySelectorAll('tr[data-student-id]');
        const attendanceData = [];

        rows.forEach((row, index) => {
            const attendanceTypeCell = row.querySelector('.attendance-type');
            const attendanceNumberCell = row.querySelector('.attendance-number');

            const studentId = row.getAttribute("data-student-id");
            const attendanceType = attendanceTypeCell.value;
            const attendanceNumber = attendanceNumberCell.value;

            if (attendanceType !== initialTableState[index].type || attendanceNumber !== initialTableState[index].number) {
                attendanceData.push({
                    student_id: studentId,
                    type: attendanceType,
                    number: attendanceNumber
                });
            }
        });

        try {
            const response = await fetch(attendanceForm.action, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(attendanceData)
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
                localStorage.removeItem('attendanceData');  // Clear local storage after successful save
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
        attendanceTableBody.querySelectorAll('tr[data-student-id]').forEach((row, index) => {
            const attendanceTypeCell = row.querySelector('.attendance-type');
            const attendanceNumberCell = row.querySelector('.attendance-number');
            attendanceTypeCell.value = initialTableState[index].type;
            attendanceNumberCell.value = initialTableState[index].number;
        });
        saveButton.style.display = "none";
        revertButton.style.display = "none";
        localStorage.removeItem('attendanceData');  // Clear local storage after reverting
    });

    function saveToLocalStorage() {
        const rows = attendanceTableBody.querySelectorAll("tr[data-student-id]");
        const data = [];

        rows.forEach((row) => {
            const attendanceTypeCell = row.querySelector('.attendance-type');
            const attendanceNumberCell = row.querySelector('.attendance-number');

            data.push({
                student_id: row.getAttribute("data-student-id"),
                type: attendanceTypeCell.value,
                number: attendanceNumberCell.value
            });
        });

        localStorage.setItem('attendanceData', JSON.stringify(data));
    }
});
