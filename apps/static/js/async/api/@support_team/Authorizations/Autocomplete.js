import domain from "../../../../_globals/domain.js";

const company_id = document.querySelector('#company_id').value;

function debounce(func, delay) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}

const autocompleteFields = [
    { id: 'clientLastName', field: 'client_last_name', datalist: 'clientLastNameSuggestions', group: 'person' },
    { id: 'clientFirstName', field: 'client_first_name', datalist: 'clientFirstNameSuggestions', group: 'person' },
    { id: 'clientLocation', field: 'client_location', datalist: 'clientLocationSuggestions', group: 'person' },
    { id: 'clientPhone', field: 'client_phone_number', displayField: 'client_phone_number_display', datalist: 'clientPhoneSuggestions', group: 'person' },
    { id: 'companyPhone', field: 'client_phone_number', displayField: 'client_phone_number_display', datalist: 'companyPhoneSuggestions', group: 'company' },
    { id: 'companyNif', field: 'company_proof_nif', displayField: 'company_proof_nif_display', datalist: 'companyNifSuggestions', group: 'company' },
    { id: 'companyRccm', field: 'company_proof_rccm', displayField: 'company_proof_rccm_display', datalist: 'companyRccmSuggestions', group: 'company' },
    { id: 'companyName', field: 'company_name', datalist: 'companyNameSuggestions', group: 'company' }
];

autocompleteFields.forEach(item => {
    const input = document.getElementById(item.id);
    if (input) {
        const debouncedInput = debounce(function(e) {
            const searchTerm = e.target.value;
            if (searchTerm.length < 2) return;
            
            fetch(`${domain}/order/v1/search-authorizations/${company_id}?term=${encodeURIComponent(searchTerm)}&field=${item.field}`)
                .then(response => response.json())
                .then(data => {
                    const datalist = document.getElementById(item.datalist);
                    if (datalist) {
                        datalist.innerHTML = '';
                        
                        data.forEach(auth => {
                            const option = document.createElement('option');
                            const displayValue = item.displayField ? auth[item.displayField] || auth[item.field] : auth[item.field] || '';
                            option.value = displayValue;
                            option.dataset.value = auth[item.field] || '';
                            option.dataset.json = JSON.stringify(auth);
                            datalist.appendChild(option);
                        });
                    }
                })
                .catch(error => console.error('Autocomplete error:', error));
        }, 300);

        input.addEventListener('input', debouncedInput);
        
        input.addEventListener('change', function(e) {
            const datalist = document.getElementById(item.datalist);
            if (!datalist) return;
            
            const selectedOption = Array.from(datalist.options).find(option => {
                const optionParts = option.value.split(' - ');
                const inputParts = e.target.value.split(' - ');
                return optionParts[0] === inputParts[0];
            });
            
            if (selectedOption && selectedOption.dataset.json) {
                try {
                    if (selectedOption.dataset.value) {
                        input.value = selectedOption.dataset.value;
                    }
                    
                    const data = JSON.parse(selectedOption.dataset.json);
                    
                    // Only update fields in the same group
                    autocompleteFields.forEach(field => {
                        // Skip the current field
                        if (field.id === item.id) return;
                        
                        // Only update fields in the same group
                        if (item.group && field.group === item.group) {
                            const el = document.getElementById(field.id);
                            if (el) {
                                // Set the actual value, not the display value
                                if (data[field.field]) {
                                    el.value = data[field.field];
                                }
                            }
                        }
                    });
                } catch (e) {
                    console.error('Error parsing autocomplete data:', e);
                }
            }
        });
    }
});