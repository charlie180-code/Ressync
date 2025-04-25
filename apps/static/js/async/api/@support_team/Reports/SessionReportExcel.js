import UtilApiURLs from "../../../../_globals/school/Report.js";
import domain from "../../../../_globals/domain.js";

document.addEventListener('DOMContentLoaded', function() {
    const exportExcelButton = document.querySelector('.export-report-excel');
    
    if (exportExcelButton) {
        exportExcelButton.addEventListener('click', function() {
            const classId = this.dataset.classId;
            const year = this.dataset.academicYearId;

            Swal.fire({
                title: 'Chargement...',
                text: 'Veuillez patienter lors de la génération des rapports Excel',
                imageUrl: `${domain}/static/img/feedbacks/hourglass.gif`,
                imageWidth: 100,
                imageHeight: 100,
                showConfirmButton: false,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            fetch(`${UtilApiURLs.GenerateExcelReports}${classId}/${year}`)
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'reports.zip';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();

                    Swal.close();
                })
                .catch(error => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'An error occurred while generating the reports. Please try again later.',
                    });
                    console.error('Error generating reports:', error);
                });
        });
    }
});
