/**
 * InstaOrbit - Profile Interactivity
 * Live avatar preview and client-side helpers
 */
document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.getElementById('avatar-input');
  const avatarPreview = document.querySelector('.avatar-preview');

  if (avatarInput && avatarPreview) {
    avatarInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (event) => {
          let img = avatarPreview.querySelector('img');
          if (!img) {
            avatarPreview.innerHTML = '';
            img = document.createElement('img');
            avatarPreview.appendChild(img);
          }
          img.src = event.target.result;
          img.style.width = '100%';
          img.style.height = '100%';
          img.style.objectFit = 'cover';
        };
        reader.readAsDataURL(file);
      }
    });
  }
});
