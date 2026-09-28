/**
 * InstaOrbit - Cosmic Direct Messaging & Real-Time WebSocket Client
 */
document.addEventListener("DOMContentLoaded", () => {
  const metadataEl = document.getElementById("chat-metadata");
  if (!metadataEl) return;

  const roomId = metadataEl.dataset.roomId;
  const currentUserId = parseInt(metadataEl.dataset.userId, 10);
  const currentUsername = metadataEl.dataset.username;
  const currentUserAvatar = metadataEl.dataset.userAvatar;

  const chatStream = document.getElementById("chat-stream");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-message-input");
  const statusBadge = document.getElementById("ws-status-badge");
  const soundToggleBtn = document.getElementById("btn-toggle-sound");
  const mobileBackBtn = document.getElementById("btn-mobile-back");
  const convSearchInput = document.getElementById("conv-search-input");
  const convList = document.getElementById("conversations-list");
  const noSearchResults = document.getElementById("search-no-results");

  // ۱. کنترل پخش صدا با Web Audio API بدون نیاز به فایل‌های صوتی سنگین
  let isMuted = localStorage.getItem("orbit_direct_muted") === "true";
  let audioCtx = null;

  function updateSoundButton() {
    if (soundToggleBtn) {
      soundToggleBtn.textContent = isMuted ? "🔇" : "🔔";
      soundToggleBtn.title = isMuted ? "فعال‌سازی صدای مخابره" : "قطع صدای مخابره";
    }
  }
  updateSoundButton();

  if (soundToggleBtn) {
    soundToggleBtn.addEventListener("click", () => {
      isMuted = !isMuted;
      localStorage.setItem("orbit_direct_muted", isMuted ? "true" : "false");
      updateSoundButton();
    });
  }

  function playSignalSound(type = "incoming") {
    if (isMuted) return;
    try {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (!audioCtx) audioCtx = new AudioCtxClass();
      if (audioCtx.state === "suspended") {
        audioCtx.resume();
      }

      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc.connect(gain);
      gain.connect(audioCtx.destination);

      if (type === "incoming") {
        // نغمه دلنشین دو مرحله‌ای کیهانی
        osc.type = "sine";
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.12); // A5
        gain.gain.setValueAtTime(0.09, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else {
        // پالس فرکانس ارسال
        osc.type = "triangle";
        osc.frequency.setValueAtTime(783.99, now); // G5
        osc.frequency.exponentialRampToValueAtTime(1046.5, now + 0.08); // C6
        gain.gain.setValueAtTime(0.07, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
        osc.start(now);
        osc.stop(now + 0.22);
      }
    } catch (e) {
      // AudioContext ممکن است قبل از تعامل کاربر مسدود شود
    }
  }

  // ۲. اسکرول خودکار به آخرین پیام
  function scrollToBottom(smooth = false) {
    if (!chatStream) return;
    if (smooth) {
      chatStream.scrollTo({
        top: chatStream.scrollHeight,
        behavior: "smooth",
      });
    } else {
      chatStream.scrollTop = chatStream.scrollHeight;
    }
  }
  scrollToBottom(false);

  // ۳. توابع کمکی برای ایمن‌سازی متن پیام و جلوگیری از XSS
  function escapeHTML(str) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(str));
    return p.innerHTML;
  }

  // ۴. اتصال وب‌سوکت در صورت انتخاب یک اتاق
  let chatSocket = null;
  let reconnectTimeout = null;

  function setConnectionStatus(status) {
    if (!statusBadge) return;
    const pulseDot = statusBadge.querySelector(".status-pulse-dot");
    const statusText = statusBadge.querySelector(".status-text");

    if (status === "connected") {
      statusBadge.style.color = "var(--accent-primary)";
      if (pulseDot) pulseDot.style.background = "var(--accent-primary)";
      if (statusText) statusText.textContent = "سیگنال پایدار";
    } else if (status === "connecting") {
      statusBadge.style.color = "var(--accent-secondary)";
      if (pulseDot) pulseDot.style.background = "var(--accent-secondary)";
      if (statusText) statusText.textContent = "در حال اتصال...";
    } else {
      statusBadge.style.color = "var(--accent-danger)";
      if (pulseDot) pulseDot.style.background = "var(--accent-danger)";
      if (statusText) statusText.textContent = "سیگنال قطع شد";
    }
  }

  function initWebSocket() {
    if (!roomId) return;

    setConnectionStatus("connecting");
    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const wsUrl = `${protocol}${window.location.host}/ws/direct/${roomId}/`;

    chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = () => {
      setConnectionStatus("connected");
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
    };

    chatSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        renderIncomingMessage(data);
      } catch (err) {
        console.error("خطا در پردازش پیام وب‌سوکت:", err);
      }
    };

    chatSocket.onclose = () => {
      setConnectionStatus("disconnected");
      // تلاش مجدد برای اتصال پس از ۳ ثانیه
      if (!reconnectTimeout) {
        reconnectTimeout = setTimeout(() => {
          initWebSocket();
        }, 3000);
      }
    };

    chatSocket.onerror = (err) => {
      console.error("خطای وب‌سوکت:", err);
      chatSocket.close();
    };
  }

  // ۵. رندر پیام جدید دریافتی یا ارسالی
  function renderIncomingMessage(data) {
    if (!chatStream) return;

    const isOutgoing = data.user_id === currentUserId;
    const timeStr = data.time || new Date().toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" });

    const msgRow = document.createElement("div");
    msgRow.className = `msg-row ${isOutgoing ? "outgoing" : "incoming"}`;

    const avatarHtml = data.avatar_url
      ? `<img src="${data.avatar_url}" alt="${escapeHTML(data.username)}" />`
      : `👨‍🚀`;

    const checkmarkHtml = isOutgoing ? `<span class="msg-check">✓✓</span>` : "";

    msgRow.innerHTML = `
      <div class="msg-avatar">
        ${avatarHtml}
      </div>
      <div class="msg-bubble">
        <div class="msg-sender-name">${escapeHTML(data.username)}</div>
        <div class="msg-text">${escapeHTML(data.message)}</div>
        <div class="msg-meta-row">
          <span>${timeStr}</span>
          ${checkmarkHtml}
        </div>
      </div>
    `;

    chatStream.appendChild(msgRow);
    scrollToBottom(true);
    playSignalSound(isOutgoing ? "outgoing" : "incoming");

    // به‌روزرسانی کارت این گفتگو در سایدبار
    updateSidebarPreview(roomId, data.message, timeStr);
  }

  // ۶. ارسال پیام هنگام سابمیت فرم
  if (chatForm && chatInput) {
    chatForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      if (!chatSocket || chatSocket.readyState !== WebSocket.OPEN) {
        alert("ارتباط با سرور مداری در حال حاضر قطع است. لطفاً کمی صبر کنید.");
        return;
      }

      chatSocket.send(JSON.stringify({ message: message }));
      chatInput.value = "";
      chatInput.focus();
    });

    // ارسال با اینتر (بدون شیفت)
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit", { cancelable: true }));
      }
    });
  }

  // ۷. درج سریع ایموجی‌های کیهانی
  document.querySelectorAll(".emoji-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      const emoji = pill.getAttribute("data-emoji");
      if (emoji && chatInput) {
        chatInput.value += emoji;
        chatInput.focus();
      }
    });
  });

  // ۸. به‌روزرسانی سایدبار و شناور کردن آخرین گفتگو به بالا
  function updateSidebarPreview(targetRoomId, text, time) {
    if (!convList) return;
    const card = convList.querySelector(`.conversation-card[data-room-id="${targetRoomId}"]`);
    if (card) {
      const snippet = card.querySelector(".conv-snippet");
      const timeEl = card.querySelector(".conv-time");
      if (snippet) snippet.textContent = text;
      if (timeEl) timeEl.textContent = time;

      // انتقال کارت به بالای لیست
      convList.prepend(card);
    }
  }

  // ۹. جستجوی زنده در لیست گفتگوها
  if (convSearchInput && convList) {
    convSearchInput.addEventListener("input", () => {
      const query = convSearchInput.value.trim().toLowerCase();
      const cards = convList.querySelectorAll(".conversation-card");
      let visibleCount = 0;

      cards.forEach((card) => {
        const username = card.getAttribute("data-username") || "";
        const fullname = card.getAttribute("data-fullname") || "";
        const matches = username.includes(query) || fullname.includes(query);

        card.style.display = matches ? "flex" : "none";
        if (matches) visibleCount++;
      });

      if (noSearchResults) {
        noSearchResults.style.display = visibleCount === 0 && query !== "" ? "flex" : "none";
      }
    });
  }

  // ۱۰. ناوبری بازگشت در نسخه موبایل
  if (mobileBackBtn) {
    mobileBackBtn.addEventListener("click", () => {
      const sidebar = document.getElementById("conversations-sidebar");
      const chatMain = document.getElementById("chat-main");
      if (sidebar && chatMain) {
        sidebar.classList.remove("hidden-mobile");
        chatMain.classList.add("hidden-mobile");
      }
    });
  }

  // شروع ارتباط وب‌سوکت در صورت وجود اتاق
  initWebSocket();
});
