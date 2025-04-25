document.addEventListener('DOMContentLoaded', function() {
    const yearFilter = document.querySelector('#yearFilter');
    const sessionTableBody = document.querySelector('#sessionTableBody');

    yearFilter.addEventListener('change', function() {
        const selectedYearId = this.value;

        fetch(`{{ url_for('session.manage_sessions', company_id=company.id) }}?year=${selectedYearId}`)
            .then(response => response.json())
            .then(data => {
                
            })
            .catch(error => console.error('Error:', error));
    });
});