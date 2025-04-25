import UtilApiURLs from '../../../../_globals/school/Report.js';
import domain from '../../../../_globals/domain.js';

document.addEventListener('DOMContentLoaded', function() {
    const printReportLink = document.querySelector('.print-report');
    
    if (printReportLink) {
        printReportLink.addEventListener('click', function() {
            const classId = this.dataset.classId;
            const sessionId = this.dataset.sessionId;

            Swal.fire({
                title: 'Chargement...',
                text: 'Veuillez patienter lors de la génération des bulletins',
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

            const timestamp = new Date().getTime(); // Current timestamp to avoid browser caching
            const reportUrl = `${UtilApiURLs.SessionReportPerClass}${classId}/${sessionId}?t=${timestamp}`;

            fetch(reportUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.blob();
                })
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
