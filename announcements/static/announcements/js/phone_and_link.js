document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.show-button').forEach(btn => {
    const label = btn.querySelector('.show-button__label');
    const anId  = btn.dataset.anId;
    const url   = btn.dataset.replaceUrl;

    btn.addEventListener('click', () => {
      if (btn.dataset.loaded === 'true') {
        const phone = btn.dataset.phone;
        return phone
          ? window.location.href = `tel:${phone}`
          : label.textContent = 'No phone number';
      }

      fetch(`${url}?an_id=${anId}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin'
      })
      .then(res => res.ok ? res.json() : Promise.reject(res.status))
      .then(data => {
        label.textContent       = data.phone;
        btn.dataset.phone       = data.phone;
        btn.dataset.loaded      = 'true';
      })
      .catch(err => {
        console.error(err);
        label.textContent = 'Error';
      });
    });
  });

  document.querySelectorAll('.show-button_link').forEach(btn => {
    const label = btn.querySelector('.show-button_link__label');
    const link  = btn.dataset.annLink;

    btn.addEventListener('click', () => {
      if (btn.dataset.clicked === 'true') {
        return link
          ? window.open(link, '_blank')
          : label.textContent = 'No link available';
      }
      label.textContent = 'View listing';
      btn.dataset.clicked = 'true';
    });
  });
});