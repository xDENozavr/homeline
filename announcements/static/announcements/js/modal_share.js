document.addEventListener('DOMContentLoaded', () => {
  const openBtns = document.querySelectorAll('#open-share-modal');
  const modal = document.getElementById('share-modal');
  const overlay = modal ? modal.querySelector('.modal-overlay') : null;
  const copyBtn = document.getElementById('copy-link-button');
  const input = document.getElementById('share-link');
  const tgLink = document.getElementById('share-telegram');
  const fbLink = document.getElementById('share-facebook');
  const twLink = document.getElementById('share-twitter');

  openBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (!modal) return;
      const pageUrl = window.location.href;
      input.value = pageUrl;
      tgLink.href = `https://t.me/share/url?url=${encodeURIComponent(pageUrl)}&text=Listing`;
      fbLink.href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(pageUrl)}`;
      twLink.href = `https://twitter.com/intent/tweet?url=${encodeURIComponent(pageUrl)}&text=Listing`;
      modal.classList.remove('hidden');
    });
  });

  if (overlay && modal) {
    overlay.addEventListener('click', () => {
      modal.classList.add('hidden');
    });
  }

  if (copyBtn && input) {
    copyBtn.addEventListener('click', () => {
      input.select();
      input.setSelectionRange(0, input.value.length);
      navigator.clipboard.writeText(input.value)
        .then(() => {
          alert('Link copied!');
        })
        .catch(err => {
          console.error('Error copying link:', err);
        });
    });
  }
});