/**
 * InstaOrbit - Theme Controller
 * Manages 4 vibrant themes (aurora, solar, ocean, sunset) with localStorage persistence
 */
(function() {
  const THEME_KEY = 'insta_orbit_theme';
  const DEFAULT_THEME = 'aurora';
  const VALID_THEMES = ['aurora', 'solar', 'ocean', 'sunset'];

  // ۱. دریافت تم ذخیره‌شده یا استفاده از تم پیش‌فرض
  function getStoredTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    return VALID_THEMES.includes(saved) ? saved : DEFAULT_THEME;
  }

  // ۲. اعمال تم روی سند HTML
  function applyTheme(themeName) {
    if (!VALID_THEMES.includes(themeName)) {
      themeName = DEFAULT_THEME;
    }
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem(THEME_KEY, themeName);

    // به‌روزرسانی وضعیت دکمه‌های انتخابگر تم
    document.querySelectorAll('.theme-dot-btn').forEach(btn => {
      const isTarget = btn.getAttribute('data-theme-name') === themeName;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-pressed', isTarget ? 'true' : 'false');
    });

    // ارسال رویداد برای کامپوننت‌های دیگر در صورت نیاز
    window.dispatchEvent(new CustomEvent('orbit:themechange', { detail: { theme: themeName } }));
  }

  // ۳. اکسپوز به پنجره عمومی
  window.setOrbitTheme = applyTheme;

  // ۴. اعمال فوری تم به محض اجرای اسکریپت (بدون پرش صفحه)
  applyTheme(getStoredTheme());

  // ۵. تنظیم لیسنرها پس از لود شدن DOM
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(getStoredTheme());

    document.querySelectorAll('.theme-dot-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const chosen = btn.getAttribute('data-theme-name');
        if (chosen) {
          applyTheme(chosen);
        }
      });
    });
  });
})();
