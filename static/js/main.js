// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('#flashMessages .alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});

// Global Toast Helper
function showToast(message, type = 'success') {
  const toastEl = document.getElementById('cnLiveToast');
  const toastText = document.getElementById('cnToastText');
  const toastIcon = document.getElementById('cnToastIcon');
  if (!toastEl || !toastText) return;

  toastEl.className = `toast align-items-center text-white border-0 shadow-lg ${type === 'success' ? 'bg-success' : type === 'warning' ? 'bg-warning text-dark' : 'bg-danger'}`;
  toastText.textContent = message;

  if (toastIcon) {
    toastIcon.className = type === 'success' ? 'bi bi-check-circle-fill fs-5' : type === 'warning' ? 'bi bi-exclamation-triangle-fill fs-5' : 'bi bi-exclamation-circle-fill fs-5';
  }

  const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 3500 });
  toast.show();
}

// Favorite toggle via AJAX
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-fav-toggle]');
  if (!btn) return;
  e.preventDefault();
  const url = btn.dataset.favToggle;
  const icon = btn.querySelector('i');
  
  fetch(url, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  })
  .then(r => r.json())
  .then(data => {
    if (data.added) {
      icon.classList.remove('bi-heart');
      icon.classList.add('bi-heart-fill');
      btn.classList.remove('btn-outline-danger');
      btn.classList.add('btn-danger');
      showToast('Property added to saved favorites! ❤️', 'success');
    } else {
      icon.classList.remove('bi-heart-fill');
      icon.classList.add('bi-heart');
      btn.classList.remove('btn-danger');
      btn.classList.add('btn-outline-danger');
      showToast('Property removed from saved favorites.', 'warning');
    }
  })
  .catch(() => { window.location.href = url; });
});

// CSRF helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    for (const cookie of document.cookie.split(';')) {
      const [k, v] = cookie.trim().split('=');
      if (k === name) { cookieValue = decodeURIComponent(v); break; }
    }
  }
  return cookieValue;
}

// Image gallery lightbox (simple)
document.querySelectorAll('.cn-gallery-thumb').forEach(img => {
  img.addEventListener('click', () => {
    const main = document.querySelector('#mainGalleryImg');
    if (main) { main.src = img.src; }
  });
});

// Star rating input
document.querySelectorAll('.cn-star-input').forEach(input => {
  input.addEventListener('change', () => {
    const val = parseInt(input.value);
    document.querySelectorAll('.cn-star-label').forEach((lbl, i) => {
      lbl.style.color = i < val ? '#F59E0B' : '#E2E8F0';
    });
  });
});

// Confirm delete dialogs
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm || 'Are you sure?')) e.preventDefault();
  });
});

// Filter collapse toggle label
const filterToggle = document.getElementById('filterToggle');
if (filterToggle) {
  filterToggle.addEventListener('click', () => {
    const icon = filterToggle.querySelector('i');
    icon.classList.toggle('bi-funnel');
    icon.classList.toggle('bi-x');
  });
}
