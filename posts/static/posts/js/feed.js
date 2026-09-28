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
});
