/**
 * InstaOrbit - Create Post Interactions
 * Drag & Drop, Live image preview, character counter
 */
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('image-input');
  const previewBox = document.getElementById('preview-container');
  const previewImg = document.getElementById('preview-img');
  const promptBox = document.getElementById('dropzone-prompt');
  const removeBtn = document.getElementById('btn-remove-image');
  const captionTextarea = document.getElementById('caption-textarea');
  const captionCounter = document.getElementById('caption-counter');

  function handleFile(file) {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        promptBox.style.display = 'none';
        previewBox.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  }

  if (dropzone && fileInput) {
    // باز کردن دیالوگ فایل با کلیک
    dropzone.addEventListener('click', (e) => {
      if (e.target !== removeBtn && !removeBtn.contains(e.target)) {
        fileInput.click();
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
      }
    });

    // رویدادهای Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        fileInput.files = files;
        handleFile(files[0]);
      }
    });
  }

  // دکمه حذف تصویر انتخاب شده
  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.value = '';
      previewImg.src = '';
      previewBox.style.display = 'none';
      promptBox.style.display = 'flex';
    });
  }

  // شمارنده کاراکترهای کپشن
  if (captionTextarea && captionCounter) {
    captionTextarea.addEventListener('input', () => {
      const len = captionTextarea.value.length;
      captionCounter.textContent = `${len} کاراکتر`;
    });
  }
});
