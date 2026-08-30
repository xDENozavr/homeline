function getCookie(name) {
  let value = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(cookie => {
      const [k, v] = cookie.trim().split('=');
      if (k === name) value = decodeURIComponent(v);
    });
  }
  return value;
}

document.addEventListener('DOMContentLoaded', () => {
  const csrftoken = getCookie('csrftoken');

  document.querySelectorAll('.fav-but').forEach(btn => {
    btn.addEventListener('click', async () => {
      const anId = btn.dataset.anId;
      const url = btn.dataset.url;
      const formData = new FormData();
      formData.append('an_id', anId);

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrftoken },
          body: formData,
        });
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        // The favorite button may or may not have an <img> inside it
        // depending on the page: on the announcement detail page it
        // does (a heart icon that toggles), but on the favorites list
        // page the button is just plain text ("Remove"). Guard every
        // img access with a null check so this works on both pages
        // without erroring out on the one that has no <img>.
        const img = btn.querySelector('img');

        if (data.action === 'added') {
          if (img) {
            img.src = img.dataset.activeSrc;
          }
          btn.classList.add('active');
          btn.setAttribute('aria-label', 'Remove from favorites');
        } else if (data.action === 'removed') {
          if (img) {
            img.src = img.dataset.defaultSrc;
          }
          btn.classList.remove('active');
          btn.setAttribute('aria-label', 'Add to favorites');

          // If the element is deleted on the favorites page, remove its card
          const card = btn.closest('.favorite-card');
          if (card) card.remove();

          // Display a message if no favorite items remain
          const list = document.querySelector('.favorites-list');
          if (list && list.querySelectorAll('.favorite-card').length === 0) {
            list.innerHTML = '<p>You have no favorite listings.</p>';
          }
        }
      } catch (error) {
        console.error('Error:', error);
      }
    });
  });
});