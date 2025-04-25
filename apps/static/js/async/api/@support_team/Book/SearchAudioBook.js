import UtilApiURLs from "../../../../_globals/general/Archive.js";

document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.getElementById('searchBar');
    const searchResults = document.getElementById('searchResults');

    searchBar.addEventListener('input', async (event) => {
        const query = event.target.value.trim();

        if (query.length > 0) {
            searchResults.classList.remove('d-none');

            try {
                const response = await fetch(`${UtilApiURLs.QueryAudiobook}?query=${encodeURIComponent(query)}`);
                const results = await response.json();

                searchResults.innerHTML = '';

                if (results.length === 0) {
                    searchResults.innerHTML = '<div class="list-group-item">No results found</div>';
                } else {
                    results.forEach(audiobook => {
                        const item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item d-flex align-items-center mb-2';
                        item.innerHTML = `
                            <img src="${audiobook.image_url || '/static/img/placeholder.png'}" alt="${audiobook.title}" class="img-thumbnail me-2 custom-thumbnail" style="width: 50px;">
                            <div>
                                <h6 class="mb-1">${audiobook.title}</h6>
                                <small class="text-muted">${audiobook.category}</small>
                            </div>
                        `;
                        searchResults.appendChild(item);
                    });
                }
            } catch (error) {
                console.error('Error:', error);
                searchResults.innerHTML = '<div class="list-group-item">Error fetching results</div>';
            }
        } else {
            searchResults.classList.add('d-none');
            searchResults.innerHTML = '';
        }
    });
});
