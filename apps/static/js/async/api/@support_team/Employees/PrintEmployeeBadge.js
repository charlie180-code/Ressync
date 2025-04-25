import domain from '../../../../_globals/domain.js';

document.getElementById('generate-badge-btn').addEventListener('click', function() {
    const employeeId = document.getElementById('employee-info').getAttribute('data-employee-id');
    const companyId = document.getElementById('company-info').getAttribute('data-company-id');

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

    fetch(`${domain}/career/v1/generate_employee_badge`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            employee_id: employeeId,
            company_id: companyId,
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Failed to generate badge');
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'employee_badge.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);        
        Swal.close();
        Swal.fire({
            title: 'Effectué!',
            text: 'Le badge a été généré avec succès.',
            icon: 'success',
            confirmButtonText: 'OK'
        });
    })
    .catch(error => {
        console.error('Error generating badge:', error);        
        Swal.close();
        Swal.fire({
            title: 'Erreur',
            text: 'Une erreur est survenue lors de la génération du badge.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    });
});
