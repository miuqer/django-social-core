/**
 * InstaOrbit - Profile Interactivity
 * Live avatar preview and network tabs (followers/following)
 */
document.addEventListener('DOMContentLoaded', () => {
  // ۱. پیش‌نمایش زنده عکس آواتار
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

  // ۲. سوییچ بین تب‌های دنبال‌کنندگان و دنبال‌شوندگان
  const tabBtns = document.querySelectorAll('.orbit-tab-btn');
  const tabFollowers = document.getElementById('tab-followers');
  const tabFollowing = document.getElementById('tab-following');

  if (tabBtns.length > 0 && tabFollowers && tabFollowing) {
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const target = btn.getAttribute('data-target');
        if (target === 'following') {
          tabFollowers.style.display = 'none';
          tabFollowing.style.display = 'flex';
        } else {
          tabFollowers.style.display = 'flex';
          tabFollowing.style.display = 'none';
        }
      });
    });
  }

  // ۳. هوشمندسازی دکمه‌های تب دنبال‌کنندگان (اتصال متقابل / قطع ارتباط)
  const followingIds = Array.isArray(window.currentFollowingIds) ? window.currentFollowingIds : [];
  document.querySelectorAll('#tab-followers .btn-network-action').forEach(btn => {
    const targetUserId = parseInt(btn.dataset.targetUserId, 10);
    if (followingIds.includes(targetUserId)) {
      btn.className = 'btn-network-action btn-network-unfollow';
      btn.innerText = 'قطع ارتباط';
      btn.setAttribute('title', 'قطع ارتباط با این مدار');
    } else {
      btn.className = 'btn-network-action btn-network-follow';
      btn.innerText = '+ اتصال متقابل';
      btn.setAttribute('title', 'دنبال کردن متقابل این مدار');
    }
  });
});
