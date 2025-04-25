import domain from '../../js/_globals/domain.js';

document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById('TransportCompanyInput');
    const suggestions = document.getElementById('TransportCompanySuggestions');
    const hiddenInput = document.getElementById('TransportCompany');
    let companies = [];

    const placeholderLogo = 'https://via.placeholder.com/30x30?text=No+Logo';

    fetch(`${domain}/wallet/v1/get-transport-companies`)
        .then(response => response.json())
        .then(data => {
            companies = data;
        })
        .catch(error => console.error('Error fetching transport companies:', error));

    const generateStars = (rating) => {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            stars += i <= rating
                ? '<span style="color: gold;">&#9733;</span>'
                : '<span style="color: lightgray;">&#9734;</span>';
        }
        return stars;
    };

    input.addEventListener('input', function () {
        const query = input.value.toLowerCase().trim();
        suggestions.innerHTML = '';
        suggestions.style.display = query ? 'block' : 'none';

        if (query) {
            const filteredCompanies = companies.filter(company =>
                company.company_name.toLowerCase().includes(query)
            );

            filteredCompanies.forEach(company => {
                const item = document.createElement('li');
                item.className = 'list-group-item d-flex align-items-center';
                item.style.cursor = 'pointer';

                const companyLogo = company.company_logo && company.company_logo !== "" 
                    ? company.company_logo 
                    : placeholderLogo;

                item.innerHTML = `
                    <div class="d-flex align-items-center">
                        <img src="${companyLogo}" alt="${company.company_name}" class="me-2" style="width: 30px; height: 30px;">
                        <div>
                            <div>${company.company_name}</div>
                            <div style="font-size: 14px;">${generateStars(company.rating)}</div>
                            <div style="font-size: 12px; color: #777;">${company.company_address}</div>
                        </div>
                    </div>
                `;
                
                item.addEventListener('click', () => {
                    input.value = company.company_name;
                    hiddenInput.value = company.company_name;
                    suggestions.style.display = 'none';
                });
                suggestions.appendChild(item);
            });
        }
    });

    document.addEventListener('click', function (e) {
        if (!suggestions.contains(e.target) && e.target !== input) {
            suggestions.style.display = 'none';
        }
    });
});
