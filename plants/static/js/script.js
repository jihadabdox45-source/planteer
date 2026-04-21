// Get favorites from localStorage
function getFavorites() {
    return JSON.parse(localStorage.getItem('favorites')) || [];
}

// Save favorites
function saveFavorites(favorites) {
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

// Update favorites count in navbar
function updateFavoritesCount() {
    const countElement = document.getElementById('favorites-count');
    if (!countElement) return;

    const favorites = getFavorites();

    if (favorites.length > 0) {
        countElement.style.display = 'inline-flex';
        countElement.textContent = favorites.length;
    } else {
        countElement.style.display = 'none';
    }
}

// Toggle favorite
function toggleFavorite(id, plantData) {
    let favorites = getFavorites();
    const index = favorites.findIndex(p => p.id === id);

    if (index > -1) {
        favorites.splice(index, 1);
    } else {
        favorites.push(plantData);
    }

    saveFavorites(favorites);
    updateFavoritesCount();
    updateButtons();
}

// Change button UI
function updateButtons() {
    const favorites = getFavorites();

    document.querySelectorAll('.add-to-favorites').forEach(btn => {
        const id = parseInt(btn.getAttribute('data-plant-id'));

        if (favorites.some(p => p.id === id)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Load favorites page
function loadFavoritesPage() {
    const container = document.getElementById('favorites-container');
    if (!container) return;

    const favorites = getFavorites();

    if (favorites.length === 0) {
        container.innerHTML = `
            <div class="text-center p-5">
                <h3>No favorites yet</h3>
                <p>Add plants to your favorites to see them here.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = '';

    favorites.forEach(plant => {
        container.innerHTML += `
            <div class="col-md-4">
                <div class="plant-card">
                    <img src="${plant.image_url}" class="card-img-top">
                    <div class="card-body">
                        <h5>${plant.name}</h5>
                        <p class="text-muted">${plant.scientific_name}</p>
                        <a href="/plants/${plant.id}/detail/" class="btn btn-outline-main w-100">
                            View Details
                        </a>
                    </div>
                </div>
            </div>
        `;
    });
}


// Run on load
document.addEventListener('DOMContentLoaded', function () {
    updateFavoritesCount();
    updateButtons();
    loadFavoritesPage();
});