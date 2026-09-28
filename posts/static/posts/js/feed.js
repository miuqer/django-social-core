/**
 * InstaOrbit - Feed Interactions
 * Handles double-click like, comment focus, and UI enhancements
 */
document.addEventListener('DOMContentLoaded', () => {
  // ۱. دابل‌کلیک روی تصاویر پست‌ها برای ثبت لایک با انیمیشن درخشان
  document.querySelectorAll('.cosmic-card').forEach(card => {
    const media = card.querySelector('.post-media');
    const likeForm = card.querySelector('.telemetry-left form');
    const commentBtn = card.querySelector('a[title="دیدگاه‌ها"]');
    const commentInput = card.querySelector('.frequency-input');

    if (media && likeForm) {
      // ساخت آیکون انیمیشن تپش
      const burst = document.createElement('div');
      burst.className = 'like-heart-burst';
      burst.innerText = '⚡';
      media.appendChild(burst);

      let lastClick = 0;
      media.addEventListener('click', (e) => {
        const now = Date.now();
        if (now - lastClick < 350) {
          // Double click detected!
          burst.classList.remove('animate');
          void burst.offsetWidth; // Trigger reflow
          burst.classList.add('animate');
          setTimeout(() => burst.classList.remove('animate'), 700);

          // ارسال خودکار فرم لایک
          likeForm.submit();
        }
        lastClick = now;
      });
    }

    // ۲. کلیک روی آیکون دیدگاه برای فوکوس نرم روی ورودی نظر
    if (commentBtn && commentInput) {
      commentBtn.addEventListener('click', (e) => {
        // اگر در همان صفحه است
        if (e.target.closest('.cosmic-card')) {
          e.preventDefault();
          commentInput.focus();
          commentInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    }
  });

  // ۳. مدیریت دکمه‌های اتصال به مدار (Follow / Unfollow)
  const followingIds = Array.isArray(window.currentFollowingIds) ? window.currentFollowingIds : [];
  document.querySelectorAll('.btn-orbit-follow').forEach(btn => {
    const targetUserId = parseInt(btn.dataset.targetUserId, 10);
    const isFollowing = followingIds.includes(targetUserId);

    if (isFollowing) {
      btn.classList.add('following');
      btn.innerHTML = '<span class="follow-icon">✓</span><span class="follow-label">در مدار</span>';
      btn.setAttribute('title', 'کلیک برای قطع ارتباط مداری');
    } else {
      btn.classList.remove('following');
      btn.innerHTML = '<span class="follow-icon">+</span><span class="follow-label">اتصال به مدار</span>';
      btn.setAttribute('title', 'دنبال کردن این مدار');
    }

    // افکت هاور برای دکمه‌هایی که در مدار هستند
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
  });
});
