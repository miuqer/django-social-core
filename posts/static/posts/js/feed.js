/**
 * InstaOrbit - Smooth Feed Interactions
 * Handles AJAX likes, follow toggle, comments focus, and cosmic story modal
 */
document.addEventListener('DOMContentLoaded', () => {
  const likedPostIds = new Set(Array.isArray(window.currentLikedPostIds) ? window.currentLikedPostIds : []);
  const followingUserIds = new Set(Array.isArray(window.currentFollowingIds) ? window.currentFollowingIds : []);

  // ۱. مقداردهی اولیه وضعیت لایک دکمه‌ها
  document.querySelectorAll('.cosmic-card').forEach(card => {
    const likeBtn = card.querySelector('.btn-like');
    if (likeBtn) {
      const postId = parseInt(likeBtn.dataset.postId, 10);
      if (likedPostIds.has(postId)) {
        likeBtn.classList.add('liked');
      }
    }
  });

  // تابع مشترک تغییر وضعیت لایک از طریق AJAX
  async function triggerLikeToggle(card) {
    const likeForm = card.querySelector('.like-form');
    const likeBtn = card.querySelector('.btn-like');
    const likesCountSpan = card.querySelector('.likes-number');
    const media = card.querySelector('.post-media');
    const burst = media ? media.querySelector('.like-heart-burst') : null;

    if (!likeForm || !likeBtn) return;

    const postId = parseInt(likeBtn.dataset.postId, 10);
    const isCurrentlyLiked = likeBtn.classList.contains('liked');

    // به‌روزرسانی آنی رابط کاربری (Optimistic UI)
    if (isCurrentlyLiked) {
      likeBtn.classList.remove('liked');
      likedPostIds.delete(postId);
      if (likesCountSpan) {
        const current = parseInt(likesCountSpan.textContent, 10) || 1;
        likesCountSpan.textContent = Math.max(0, current - 1);
      }
    } else {
      likeBtn.classList.add('liked', 'pulse');
      likedPostIds.add(postId);
      setTimeout(() => likeBtn.classList.remove('pulse'), 500);

      if (likesCountSpan) {
        const current = parseInt(likesCountSpan.textContent, 10) || 0;
        likesCountSpan.textContent = current + 1;
      }

      // انیمیشن تپش کوانتومی روی عکس
      if (burst) {
        burst.classList.remove('animate');
        void burst.offsetWidth; // Trigger reflow
        burst.classList.add('animate');
        setTimeout(() => burst.classList.remove('animate'), 700);
      }
    }

    // ارسال درخواست پس‌زمینه بدون رفرش صفحه
    try {
      await fetch(likeForm.action, {
        method: 'POST',
        body: new FormData(likeForm),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
    } catch (err) {
      console.warn('Like signal could not be transmitted:', err);
    }
  }

  // ۲. کنترل کارت‌های پست (دابل‌کلیک، دکمه لایک، فوکوس نظر)
  document.querySelectorAll('.cosmic-card').forEach(card => {
    const media = card.querySelector('.post-media');
    const likeForm = card.querySelector('.like-form');
    const likeBtn = card.querySelector('.btn-like');
    const commentBtn = card.querySelector('a[title="دیدگاه‌ها"]');
    const commentInput = card.querySelector('.frequency-input');

    if (media && likeForm) {
      // ایجاد المان انیمیشن جرقه لایک
      let burst = media.querySelector('.like-heart-burst');
      if (!burst) {
        burst = document.createElement('div');
        burst.className = 'like-heart-burst';
        burst.innerText = '⚡';
        media.appendChild(burst);
      }

      let lastClickTime = 0;
      media.addEventListener('click', (e) => {
        const now = Date.now();
        if (now - lastClickTime < 380) {
          // دابل‌کلیک ثبت شد
          triggerLikeToggle(card);
        }
        lastClickTime = now;
      });
    }

    if (likeBtn && likeForm) {
      likeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        triggerLikeToggle(card);
      });
    }

    if (commentBtn && commentInput) {
      commentBtn.addEventListener('click', (e) => {
        if (e.target.closest('.cosmic-card')) {
          e.preventDefault();
          commentInput.focus();
          commentInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    }
  });

  // ۳. مدیریت تعاملی دکمه‌های فالو/آنفالو بدون رفرش صفحه
  function updateFollowButtonVisual(btn, isFollowing) {
    if (isFollowing) {
      btn.classList.add('following');
      btn.innerHTML = '<span class="follow-icon">✓</span><span class="follow-label">در مدار</span>';
      btn.setAttribute('title', 'کلیک برای قطع ارتباط مداری');
    } else {
      btn.classList.remove('following');
      btn.innerHTML = '<span class="follow-icon">+</span><span class="follow-label">اتصال به مدار</span>';
      btn.setAttribute('title', 'دنبال کردن این مدار');
    }
  }

  document.querySelectorAll('.btn-orbit-follow').forEach(btn => {
    const targetUserId = parseInt(btn.dataset.targetUserId, 10);
    const isFollowing = followingUserIds.has(targetUserId);

    updateFollowButtonVisual(btn, isFollowing);

    btn.addEventListener('mouseenter', () => {
      if (btn.classList.contains('following')) {
        btn.innerHTML = '<span class="follow-icon">✕</span><span class="follow-label">قطع ارتباط</span>';
      }
    });

    btn.addEventListener('mouseleave', () => {
      if (btn.classList.contains('following')) {
        btn.innerHTML = '<span class="follow-icon">✓</span><span class="follow-label">در مدار</span>';
      }
    });

    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const willFollow = !btn.classList.contains('following');

      if (willFollow) {
        followingUserIds.add(targetUserId);
      } else {
        followingUserIds.delete(targetUserId);
      }

      // به‌روزرسانی تمام دکمه‌های مربوط به همین کاربر در صفحه
      document.querySelectorAll(`.btn-orbit-follow[data-target-user-id="${targetUserId}"]`).forEach(b => {
        updateFollowButtonVisual(b, willFollow);
      });

      // ارسال درخواست بدون بارگذاری مجدد
      try {
        await fetch(btn.href, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
      } catch (err) {
        console.warn('Network sync failed:', err);
      }
    });
  });

  // ۴. مدال تعاملی استوری‌های فضایی
  let storyModal = document.querySelector('.cosmic-story-modal');
  if (!storyModal) {
    storyModal = document.createElement('div');
    storyModal.className = 'cosmic-story-modal';
    storyModal.innerHTML = `
      <div class="story-viewer-card">
        <div class="story-progress-bar-container">
          <div class="story-progress-bar"><div class="story-progress-fill"></div></div>
        </div>
        <div class="story-viewer-header">
          <div class="story-viewer-user">
            <span class="story-modal-avatar">🛰️</span>
            <span class="story-modal-name">ایستگاه فضایی</span>
          </div>
          <button type="button" class="btn-close-story">✕</button>
        </div>
        <div class="story-viewer-body">
          <div class="story-large-icon">🌌</div>
          <p class="story-msg">در حال دریافت سیگنال‌های مستقیم از عمق مدار...</p>
        </div>
      </div>
    `;
    document.body.appendChild(storyModal);
  }

  let storyTimer = null;
  let progressInterval = null;

  function closeStory() {
    storyModal.classList.remove('active');
    clearTimeout(storyTimer);
    clearInterval(progressInterval);
    const fill = storyModal.querySelector('.story-progress-fill');
    if (fill) fill.style.width = '0%';
  }

  const closeBtn = storyModal.querySelector('.btn-close-story');
  if (closeBtn) closeBtn.addEventListener('click', closeStory);

  storyModal.addEventListener('click', (e) => {
    if (e.target === storyModal) closeStory();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && storyModal.classList.contains('active')) {
      closeStory();
    }
  });

  document.querySelectorAll('.story-item').forEach(item => {
    item.addEventListener('click', () => {
      const name = item.querySelector('.story-username')?.textContent.trim() || 'فضانورد مدار';
      const avatarText = item.querySelector('.story-avatar')?.textContent.trim() || '🛰️';

      storyModal.querySelector('.story-modal-name').textContent = name;
      storyModal.querySelector('.story-large-icon').textContent = avatarText.length > 2 ? '🪐' : avatarText;
      storyModal.querySelector('.story-msg').textContent = `سیگنال مخابره زنده از ${name}`;

      const fill = storyModal.querySelector('.story-progress-fill');
      fill.style.width = '0%';

      storyModal.classList.add('active');

      let progress = 0;
      clearInterval(progressInterval);
      clearTimeout(storyTimer);

      progressInterval = setInterval(() => {
        progress += 2;
        fill.style.width = `${progress}%`;
        if (progress >= 100) {
          clearInterval(progressInterval);
        }
      }, 70);

      storyTimer = setTimeout(closeStory, 3700);
    });
  });
});
