const searchFileForm = document.querySelector('#folderSearchForm');
const searchInput = document.getElementById('folderSearchInput');
const searchResultsDropdown = document.getElementById('searchResultsDropdown');
const folderTable = document.getElementById('folderTable');

searchInput.addEventListener('input', function() {
    let query = this.value;
    if (query.length > 0) {
        fetchSearchResults(query);
        folderTable.classList.add('d-none');
    } else {
        searchResultsDropdown.classList.add('d-none');
        folderTable.classList.remove('d-none');
    }
});

function fetchSearchResults(query) {
    fetch(`${searchFileForm.action}?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            let resultsContainer = searchResultsDropdown;
            resultsContainer.innerHTML = '';
            if (data.results.length > 0) {
                data.results.forEach(result => {
                    let item = document.createElement('a');
                    item.href = result.url;
                    item.className = 'search-result d-flex align-items-center';
                    item.style = 'padding: 10px; border: 1px solid #ddd; margin-bottom: 10px;';

                    let labelHighlighted = result.label.replace(new RegExp(query, 'gi'), match => `<span class="highlight">${match}</span>`);

                    item.innerHTML = `
                        <div class="d-flex align-items-center">
                            ${result.icon}
                            <div>
                                <h6 class="mb-1">${labelHighlighted}</h6>
                                <small class="text-muted">${result.type}</small>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">${result.folder_name}</small>
                        </div>`;
                    
                    resultsContainer.appendChild(item);
                });
                resultsContainer.classList.remove('d-none');
            } else {
                resultsContainer.innerHTML = `<p class="text-center">No results found for "<span class="highlight">${query}</span>"</p>`;
                resultsContainer.classList.remove('d-none');
            }
        });
}