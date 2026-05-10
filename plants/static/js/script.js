// Toggle favorite with database support
function toggleFavorite(button) {
    const plantId = button.getAttribute('data-plant-id');
    
    // Send request to server
    fetch(`/plants/${plantId}/toggle-favorite/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateButtonState(button, data.is_favorite);
            showNotification(data.message);
        } else if (data.error === 'authentication_required') {
            // Redirect to login if not authenticated
            window.location.href = data.redirect_url;
        } else {
            showNotification('Error updating favorites', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating favorites', 'error');
    });
}

// Update button state
function updateButtonState(button, isFavorite) {
    // Check if this is a text button (has px-3 class) or icon-only button
    const isTextButton = button.classList.contains('px-3');
    
    if (isTextButton) {
        // Text button (in plant detail page)
        if (isFavorite) {
            button.style.background = '#dc3545';
            button.style.color = 'white';
            button.innerHTML = '<i class="bi bi-heart-fill me-1"></i> Remove from Favorites';
        } else {
            button.style.background = '#6c757d';
            button.style.color = 'white';
            button.innerHTML = '<i class="bi bi-heart-fill me-1"></i> Add to Favorites';
        }
    } else {
        // Icon-only button (in cards)
        if (isFavorite) {
            button.style.background = 'rgba(220, 53, 69, 0.95)';
            button.style.borderColor = '#dc3545';
            button.innerHTML = '<i class="bi bi-heart-fill" style="font-size: 1rem; color: white;"></i>';
            button.title = 'Remove from favorites';
        } else {
            button.style.background = 'rgba(255, 255, 255, 0.95)';
            button.style.borderColor = '#e5e7eb';
            button.innerHTML = '<i class="bi bi-heart-fill" style="font-size: 1rem; color: #6b7280;"></i>';
            button.title = 'Add to favorites';
        }
    }
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show notification
function showNotification(message, type = 'success') {
    // Remove existing notification
    const existing = document.querySelector('.favorite-notification');
    if (existing) existing.remove();

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3 favorite-notification`;
    notification.style.zIndex = '9999';
    notification.style.minWidth = '250px';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('Favorites script loaded!');

    // Add click event to all favorite buttons
    document.querySelectorAll('.add-to-favorites').forEach(btn => {
        btn.addEventListener('click', function() {
            toggleFavorite(this);
        });
    });
    
    // Initialize button states for authenticated users
    initializeFavoriteButtons();
});

// Initialize favorite buttons state
function initializeFavoriteButtons() {
    // This function can be used to set initial states if needed
    // For now, the server-side template handles the initial state
}
