document.addEventListener('DOMContentLoaded', () => {
  const streetInput = document.getElementById('street_input');
  const streetTable = document.getElementById('street_table');
  const streetBtn   = document.getElementById('street-search-btn');

  if (streetInput && streetTable && streetBtn) {
    streetTable.querySelectorAll('tbody tr').forEach(row => row.style.display = 'none');
    streetBtn.addEventListener('click', () => {
      const filterText = streetInput.value.trim().toLowerCase();
      streetTable.querySelectorAll('tbody tr').forEach(row => {
        const name = row.cells[0].textContent.toLowerCase();
        row.style.display = filterText && name.includes(filterText) ? '' : 'none';
      });
    });
  }

  const rdBtn = document.getElementById('rooms-district-btn');
  if (rdBtn) {
    rdBtn.addEventListener('click', async () => {
      const form = document.getElementById('rooms-district-form');
      const params = new URLSearchParams(new FormData(form));
      const response = await fetch(`${window.location.pathname}?${params}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const newContent = doc.querySelector('#room_district-result').innerHTML;
      document.getElementById('room_district-result').innerHTML = newContent;
    });
  }

  const rsBtn = document.getElementById('rooms-street-btn');
  if (rsBtn) {
    rsBtn.addEventListener('click', async () => {
      const form = document.getElementById('rooms-street-form');
      const params = new URLSearchParams(new FormData(form));
      const response = await fetch(`${window.location.pathname}?${params}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const newContent = doc.querySelector('#room_street-result').innerHTML;
      document.getElementById('room_street-result').innerHTML = newContent;
    });
  }
});
