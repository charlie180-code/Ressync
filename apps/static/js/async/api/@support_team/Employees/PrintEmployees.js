import domain from '../../../../_globals/domain.js'

document.querySelector('.export-report-pdf').addEventListener('click', function() {
    downloadEmployeeList('pdf');
});

document.querySelector('.export-report-excel').addEventListener('click', function() {
    downloadEmployeeList('excel');
});

document.querySelector('.export-report-docx').addEventListener('click', function() {
    downloadEmployeeList('docx');
});

function downloadEmployeeList(format) {
    const companyId = document.getElementById('company-info').getAttribute('data-company-id');
    const pipelineId = getSelectedPipelineId();

    const url = `${domain}/career/v1/download_employee_list?company_id=${companyId}&format=${format}&pipeline_id=${pipelineId}`;

    Swal.fire({
        title: 'Chargement...',
        text: 'Veuillez patienter',
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

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `employee_list.${format}`;
        link.click(); 
        window.URL.revokeObjectURL(url);

        Swal.close();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        Swal.close();
    });
}

function getSelectedPipelineId() {
    const pipelineSelect = document.getElementById('pipeline-select');
    return pipelineSelect ? pipelineSelect.value : null;
}
