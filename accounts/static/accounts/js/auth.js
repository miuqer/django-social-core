/**
 * InstaOrbit - Authentication & Security Interactivity
 * Handles show/hide password toggle, live password matching, and sleek UX
 */
document.addEventListener('DOMContentLoaded', () => {
  // ۱. دکمه نمایش / پنهان‌سازی گذرواژه
  document.querySelectorAll('.btn-toggle-pw').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const container = btn.closest('.password-field-container') || btn.parentElement;
      const input = container.querySelector('input');
      const icon = btn.querySelector('.pw-eye-icon');

      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          if (icon) icon.textContent = '🙈';
          btn.setAttribute('title', 'مخفی‌سازی گذرواژه');
        } else {
          input.type = 'password';
          if (icon) icon.textContent = '👁️';
          btn.setAttribute('title', 'نمایش گذرواژه');
        }
      }
    });
  });

  // ۲. اعتبارسنجی زنده تطابق گذرواژه در صفحات ثبت‌نام و بازنشانی
  const pwInput = document.querySelector('input[name="password"], input[name="new_password"]');
  const confirmPwInput = document.querySelector('input[name="confirm_password"]');

  if (pwInput && confirmPwInput) {
    const checkMatch = () => {
      if (!confirmPwInput.value) {
        confirmPwInput.style.borderColor = '';
        return;
      }
      if (pwInput.value === confirmPwInput.value) {
        confirmPwInput.style.borderColor = 'var(--accent-primary)';
      } else {
        confirmPwInput.style.borderColor = 'var(--accent-danger)';
      }
    };

    pwInput.addEventListener('input', checkMatch);
    confirmPwInput.addEventListener('input', checkMatch);
  }

  // ۳. انیمیشن بازخورد ارسال فرم
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('.btn-submit');
      if (submitBtn) {
        submitBtn.style.opacity = '0.75';
        submitBtn.style.pointerEvents = 'none';
        submitBtn.innerText = 'در حال مخابره به مدار... 🛰️';
      }
    });
  });
});
