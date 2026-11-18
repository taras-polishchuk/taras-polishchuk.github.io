/* ============================================================
   AI Portfolio Assistant — chat widget
   Connects to n8n Chat Trigger webhook.
   Hardened v2 (2026-06-21):
     - domain-restricted prompts (no company/role/Shopify quick prompts)
     - prompt-injection resistance (pre-LLM guard on server)
     - session isolation (crypto-strong session ID, 128-bit)
     - cost protection (input cap 500, rate limit 5/min & 30/hr, max 50 msgs/session)
     - identity protection (system message armor + post-LLM guard)
   Webhook ID (regenerated on n8n restart): 0c620ad2-9b69-4484-a56f-5c1eddc47ead
   // Tunnel URL rotated 2026-07-02 (was: finishing-smart-celebs-graduates — DEAD/NXDOMAIN)
   ============================================================ */
(function () {
  'use strict';

  // ============================================================
  // Versioning & localStorage migration
  // ============================================================
  // WIDGET_VERSION is exposed on window so support code (e.g. bug reports)
  // can read which build is loaded. Bump it whenever the widget changes
  // in a user-visible way, AND whenever STORAGE_KEY / STORAGE_RATE_KEY /
  // STORAGE_COUNT_KEY schema changes — that triggers a flush-and-restart.
  const WIDGET_VERSION = '2.1.1';
  const STORAGE_VERSION_KEY = 'taras-ai-widget-version';

  // If the on-disk widget version differs from the running version, nuke
  // history / rate / count state so the user immediately sees the new
  // welcome message and fresh limits — instead of being stuck on a stale
  // "Why Rentberry?" placeholder or out-of-date quick prompts that were
  // stored before the v2 hardening.
  function _migrateStorage() {
    try {
      const onDisk = localStorage.getItem(STORAGE_VERSION_KEY);
      if (onDisk === WIDGET_VERSION) return;
      // Different version → flush user-visible state.
      // (Keep SESSION_ID — it's safe to carry across widget builds.)
      localStorage.removeItem('taras-ai-chat-history-v1');
      localStorage.removeItem('taras-ai-rate-v2');
      localStorage.removeItem('taras-ai-msgcount-v2');
      // Also nuke legacy v1 keys that the pre-hardening widget used.
      localStorage.removeItem('taras-ai-history');
      localStorage.removeItem('taras-ai-rate');
      localStorage.removeItem('taras-ai-msgcount');
      localStorage.setItem(STORAGE_VERSION_KEY, WIDGET_VERSION);
    } catch (e) {
      /* private mode / quota — ignore */
    }
  }
  _migrateStorage();

  // ============================================================
  // n8n Chat Trigger webhook URL
  // ============================================================
  // The Cloudflare Named Tunnel routes chat.taraspolishchuk.com -> n8n:5678.
  // This URL is STABLE — no more rotating trycloudflare.com subdomains.
  // Migration completed 2026-07-10 (mission portfolio-chat-production-2026-07-10).
  // See homelab/scripts/healthcheck-chat-tunnel.sh for liveness probe.
  const N8N_WEBHOOK_URL =
    'https://chat.taraspolishchuk.com/webhook/0c620ad2-9b69-4484-a56f-5c1eddc47ead/chat';

  const STORAGE_KEY = 'taras-ai-chat-history-v1';
  // ----- Hardening constants (v2: production hardening, 2026-06-21) -----
  // Cost protection: cap input size, rate-limit per session, max messages per session.
  const MAX_INPUT = 500;
  const MAX_MESSAGES_PER_SESSION = 50;
  const RATE_LIMIT_PER_MIN = 5;
  const RATE_LIMIT_PER_HOUR = 30;
  const RATE_WINDOW_MIN_MS = 60 * 1000;
  const RATE_WINDOW_HOUR_MS = 60 * 60 * 1000;
  const STORAGE_RATE_KEY = 'taras-ai-rate-v2';
  const STORAGE_COUNT_KEY = 'taras-ai-msgcount-v2';

  // Session ID: cryptographically random 128-bit value, base36.
  // Replaces prior Math.random (weak) generator.
  function _newSessionId() {
    const arr = new Uint8Array(16);
    (self.crypto || self.msCrypto).getRandomValues(arr);
    return 'sess-' + Array.from(arr, (b) => b.toString(16).padStart(2, '0')).join('');
  }
  const SESSION_ID = (() => {
    let v = localStorage.getItem('taras-ai-session');
    if (!v || !/^sess-[0-9a-f]{32}$/.test(v)) {
      v = _newSessionId();
      localStorage.setItem('taras-ai-session', v);
    }
    return v;
  })();

  // Rate-limit state (windowed counters, per session).
  function _loadRate() {
    try {
      const raw = localStorage.getItem(STORAGE_RATE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }
  function _saveRate(arr) {
    try {
      localStorage.setItem(STORAGE_RATE_KEY, JSON.stringify(arr.slice(-200)));
    } catch (e) {
      /* quota or private mode — ignore */
    }
  }
  function _rateCheck(now) {
    const log = _loadRate();
    // drop entries outside both windows
    const fresh = log.filter((t) => now - t < RATE_WINDOW_HOUR_MS);
    const minCount = fresh.filter((t) => now - t < RATE_WINDOW_MIN_MS).length;
    const hourCount = fresh.length;
    if (minCount >= RATE_LIMIT_PER_MIN) {
      return { ok: false, reason: 'rate_limit_min', retryMs: RATE_WINDOW_MIN_MS - (now - fresh[fresh.length - RATE_LIMIT_PER_MIN]) };
    }
    if (hourCount >= RATE_LIMIT_PER_HOUR) {
      return { ok: false, reason: 'rate_limit_hour', retryMs: RATE_WINDOW_HOUR_MS - (now - fresh[0]) };
    }
    return { ok: true, log: fresh };
  }
  function _rateRecord(now, log) {
    log.push(now);
    _saveRate(log);
  }
  function _getMsgCount() {
    try {
      return parseInt(localStorage.getItem(STORAGE_COUNT_KEY) || '0', 10) || 0;
    } catch (e) {
      return 0;
    }
  }
  function _setMsgCount(n) {
    try {
      localStorage.setItem(STORAGE_COUNT_KEY, String(n));
    } catch (e) {
      /* ignore */
    }
  }

  /* ---------- styles (injected, scoped under #ai-assistant-root) ---------- */
const CSS = `
  #ai-assistant-root { all: initial; }
  #ai-assistant-root * { box-sizing: border-box; }
  #ai-assistant-root {
    --g-font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Helvetica Neue", Helvetica, Arial, sans-serif;
    --g-accent: #0a84ff;
    --g-accent-2: #0071e3;
    --g-text: #f5f5f7;
    --g-text-2: rgba(245, 245, 247, 0.72);
    --g-text-3: rgba(245, 245, 247, 0.45);
    --g-glass: rgba(28, 28, 30, 0.62);
    --g-glass-strong: rgba(44, 44, 46, 0.72);
    --g-border: rgba(255, 255, 255, 0.18);
    --g-highlight: rgba(255, 255, 255, 0.42);
    --g-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
    --g-ease: cubic-bezier(0.28, 0, 0.22, 1);
  }

  /* Liquid Glass FAB */
  .ai-fab {
    position: fixed;
    right: 20px;
    bottom: 20px;
    z-index: 9998;
    width: 58px;
    height: 58px;
    border-radius: 9999px;
    background: var(--g-glass);
    border: 1px solid var(--g-border);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    backdrop-filter: blur(24px) saturate(180%);
    cursor: pointer;
    box-shadow: inset 0 1px 0 var(--g-highlight), 0 10px 30px rgba(0, 0, 0, 0.35);
    transition: transform 220ms var(--g-ease), box-shadow 220ms var(--g-ease), background 150ms;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-family: var(--g-font);
  }
  .ai-fab::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: radial-gradient(circle at 30% 25%, rgba(255,255,255,0.28), rgba(255,255,255,0) 55%);
    pointer-events: none;
  }
  .ai-fab:hover { transform: scale(1.06); background: var(--g-glass-strong); box-shadow: inset 0 1px 0 var(--g-highlight), 0 14px 36px rgba(0, 0, 0, 0.4), 0 0 0 6px rgba(10, 132, 255, 0.12); }
  .ai-fab:active { transform: scale(0.96); }
  .ai-fab:focus-visible { outline: none; box-shadow: inset 0 1px 0 var(--g-highlight), 0 0 0 4px rgba(10, 132, 255, 0.45); }
  .ai-fab[aria-expanded="true"] { transform: rotate(90deg); }

  .ai-fab-badge {
    position: absolute;
    top: -2px;
    right: -2px;
    background: var(--g-accent);
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    line-height: 1;
    padding: 4px 6px;
    border-radius: 9999px;
    box-shadow: 0 0 0 2px rgba(0,0,0,0.6);
    pointer-events: none;
  }
  .ai-fab-badge[hidden] { display: none; }

  /* HI-4: visible "Chat with AI" label next to the fab on first visit,
     then fades. Recruiters learn the fab is interactive, not a decorative orb. */
  .ai-fab-label {
    position: fixed;
    right: 90px;
    bottom: 31px;
    z-index: 9997;
    background: var(--g-glass);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    backdrop-filter: blur(20px) saturate(180%);
    color: var(--g-text);
    font-size: 13px;
    font-weight: 500;
    padding: 9px 14px;
    border-radius: 9999px;
    border: 1px solid var(--g-border);
    box-shadow: inset 0 1px 0 var(--g-highlight), 0 8px 24px rgba(0, 0, 0, 0.35);
    pointer-events: none;
    opacity: 0;
    transform: translateX(8px);
    transition: opacity 0.4s var(--g-ease), transform 0.4s var(--g-ease);
    white-space: nowrap;
    font-family: var(--g-font);
  }
  .ai-fab-label.visible { opacity: 1; transform: translateX(0); }
  .ai-fab-label::after { content: none; }

  /* Glass panel */
  .ai-panel {
    position: fixed;
    right: 20px;
    bottom: 92px;
    z-index: 9999;
    width: min(390px, calc(100vw - 32px));
    height: min(640px, calc(100vh - 120px));
    background: var(--g-glass);
    -webkit-backdrop-filter: blur(36px) saturate(190%);
    backdrop-filter: blur(36px) saturate(190%);
    border: 1px solid var(--g-border);
    border-radius: 26px;
    box-shadow: inset 0 1px 0 var(--g-highlight), inset 0 -1px 0 rgba(255,255,255,0.06), var(--g-shadow);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    opacity: 0;
    transform: translateY(14px) scale(0.98);
    pointer-events: none;
    transition: opacity 220ms var(--g-ease), transform 260ms var(--g-ease);
    font-family: var(--g-font);
    color: var(--g-text);
    -webkit-font-smoothing: antialiased;
  }
  .ai-panel[data-open="true"] {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: auto;
  }
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    .ai-panel, .ai-fab, .ai-fab-label { background: rgba(28, 28, 30, 0.96); }
  }

  .ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 14px 14px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.10);
    background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0) 100%);
  }
  .ai-header-avatar {
    width: 36px;
    height: 36px;
    border-radius: 9999px;
    background: linear-gradient(145deg, #3a8dff 0%, #0a84ff 60%, #0060df 100%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.45), 0 4px 12px rgba(10, 132, 255, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    color: #fff;
    flex-shrink: 0;
  }
  .ai-header-meta { flex: 1; min-width: 0; }
  .ai-book {
    flex-shrink: 0;
    padding: 7px 13px;
    border-radius: 9999px;
    background: #fff;
    color: #1d1d1f;
    font-size: 12px;
    font-weight: 600;
    text-decoration: none;
    white-space: nowrap;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    transition: transform 150ms var(--g-ease), background 150ms;
  }
  .ai-book:hover { background: #f5f5f7; }
  .ai-book:active { transform: scale(0.96); }
  .ai-book:focus-visible { outline: none; box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.45); }
  .ai-header-title {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.2;
    margin: 0;
    letter-spacing: -0.01em;
  }
  .ai-header-status {
    font-size: 11px;
    color: var(--g-text-2);
    margin: 2px 0 0 0;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .ai-header-status::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: #30d158;
    box-shadow: 0 0 0 3px rgba(48, 209, 88, 0.22);
  }
  .ai-header-status[data-state="error"] { color: #ff6b6b; }
  .ai-header-status[data-state="error"]::before { background: #ff453a; box-shadow: 0 0 0 3px rgba(255, 69, 58, 0.22); }
  .ai-close {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.10);
    cursor: pointer;
    width: 30px;
    height: 30px;
    padding: 0;
    border-radius: 9999px;
    color: var(--g-text-2);
    transition: background 150ms, color 150ms;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .ai-close:hover { background: rgba(255, 255, 255, 0.16); color: #fff; }
  .ai-close:focus-visible { outline: none; box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.45); }

  .ai-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }
  .ai-messages::-webkit-scrollbar { width: 6px; }
  .ai-messages::-webkit-scrollbar-track { background: transparent; }
  .ai-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.18); border-radius: 3px; }

  .ai-msg {
    max-width: 86%;
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.4;
    word-wrap: break-word;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
    letter-spacing: -0.01em;
    animation: ai-msg-in 240ms var(--g-ease);
  }
  @keyframes ai-msg-in {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .ai-msg-user {
    align-self: flex-end;
    background: linear-gradient(180deg, #2b8fff 0%, #0a84ff 100%);
    color: #fff;
    border-bottom-right-radius: 6px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.3);
  }

  .ai-msg-bot {
    align-self: flex-start;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.10);
    color: var(--g-text);
    border-bottom-left-radius: 6px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.14);
  }

  .ai-msg-error {
    align-self: flex-start;
    background: rgba(255, 69, 58, 0.14);
    border: 1px solid rgba(255, 69, 58, 0.3);
    color: #ff9f98;
    border-bottom-left-radius: 6px;
    font-size: 13px;
  }

  .ai-msg-meta {
    font-size: 10px;
    color: var(--g-text-3);
    margin-top: 4px;
    text-align: right;
  }
  .ai-msg-bot .ai-msg-meta { text-align: left; }
  .ai-msg .ai-msg-link { color: #6cb5ff; text-decoration: underline; text-underline-offset: 2px; word-break: break-all; }
  .ai-msg-user .ai-msg-link { color: #fff; }

  .ai-typing {
    align-self: flex-start;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    border-bottom-left-radius: 6px;
  }
  .ai-typing-dot {
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: var(--g-text-2);
    animation: ai-typing 1.4s infinite ease-in-out;
  }
  .ai-typing-dot:nth-child(2) { animation-delay: 0.16s; }
  .ai-typing-dot:nth-child(3) { animation-delay: 0.32s; }
  @keyframes ai-typing {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-4px); opacity: 1; }
  }

  .ai-quick {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 0 16px 12px;
  }
  .ai-quick-btn {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: var(--g-text);
    font-size: 12.5px;
    font-weight: 500;
    padding: 7px 12px;
    border-radius: 9999px;
    cursor: pointer;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.14);
    transition: background 150ms, border-color 150ms, transform 150ms var(--g-ease);
    font-family: inherit;
  }
  .ai-quick-btn:hover {
    background: rgba(255, 255, 255, 0.16);
    border-color: rgba(255, 255, 255, 0.28);
  }
  .ai-quick-btn:active { transform: scale(0.97); }
  .ai-quick-btn:focus-visible { outline: none; box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.45); }
  .ai-quick[hidden] { display: none; }

  .ai-input-row {
    display: flex;
    gap: 8px;
    padding: 12px 12px 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.10);
    background: rgba(0, 0, 0, 0.18);
  }
  .ai-input {
    flex: 1;
    min-width: 0;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: var(--g-text);
    /* font-size 16px is REQUIRED on iOS: WebKit auto-zooms the viewport
       on focus for any text input with computed font-size < 16px and
       does NOT reset the scale on blur, leaving the page stuck zoomed in.
       This MUST stay at 16px for any text input inside the panel. */
    font-size: 16px;
    font-family: inherit;
    padding: 9px 14px;
    border-radius: 20px;
    resize: none;
    /* Single-line visual: scroll only when user types Enter for newline.
       overflow-y: hidden kills the inner WebKit scrollbar; we manage
       line count in JS (autosizeInput) instead. max-height caps the
       textarea at ~5 lines if JS grows it. */
    overflow-y: hidden;
    overflow-x: hidden;
    max-height: 120px;
    line-height: 1.3;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.10);
    transition: border-color 150ms, background 150ms;
    /* Prevent inherited zoom on iOS Safari (iOS 16+). */
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
  }
  /* Placeholder can stay smaller: it is NOT focused, so it does not
     trigger iOS auto-zoom. This frees horizontal space so the hint
     fits on one line in narrow mobile viewports. */
  .ai-input::placeholder {
    color: var(--g-text-3);
    font-size: 13px;
  }
  /* Belt-and-suspenders: kill any webkit scrollbar that could appear
     on the textarea itself (Safari sometimes shows a thin bar when
     content overflows before JS autosizes). */
  .ai-input::-webkit-scrollbar { width: 0; height: 0; display: none; }
  .ai-input { scrollbar-width: none; }
  .ai-input:focus {
    outline: none;
    border-color: rgba(10, 132, 255, 0.8);
    background: rgba(255, 255, 255, 0.14);
  }
  .ai-input:disabled { opacity: 0.6; cursor: not-allowed; }

  .ai-send {
    background: var(--g-accent);
    border: none;
    color: #fff;
    font-weight: 600;
    width: 40px;
    height: 40px;
    padding: 0;
    border-radius: 9999px;
    cursor: pointer;
    font-size: 13px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.3), 0 4px 12px rgba(10, 132, 255, 0.35);
    transition: transform 150ms var(--g-ease), opacity 150ms, background 150ms;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    align-self: flex-end;
  }
  .ai-send:hover:not(:disabled) { background: #2b8fff; }
  .ai-send:active:not(:disabled) { transform: scale(0.94); }
  .ai-send:disabled { opacity: 0.4; cursor: not-allowed; box-shadow: none; }
  .ai-send:focus-visible { outline: none; box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.45); }
  .ai-send svg { width: 16px; height: 16px; }

  .ai-footer {
    text-align: center;
    font-size: 10px;
    color: var(--g-text-3);
    padding: 6px 6px calc(6px + env(safe-area-inset-bottom));
    background: rgba(0, 0, 0, 0.18);
  }
  .ai-footer a { color: var(--g-text-2); text-decoration: none; }
  .ai-footer a:hover { color: #fff; }

  @media (max-width: 480px) {
    .ai-panel {
      right: 0;
      bottom: 0;
      width: 100vw;
      height: 100dvh;
      max-height: 100dvh;
      border-radius: 0;
      border: none;
      background: rgba(20, 20, 22, 0.94);
    }
    .ai-header { padding-top: calc(14px + env(safe-area-inset-top)); }
    .ai-fab[data-mobile="true"] { display: none; }
  }
  @media (prefers-reduced-motion: reduce) {
    .ai-panel, .ai-fab, .ai-msg, .ai-fab-label { transition: none; animation: none; }
  }
  `;

  // Welcome: portfolio-only topics, no company/Shopify mention (hardening v2).
  const BOOKING_URL = 'https://calendar.app.google/VN55jao7H4GcvMqq5';
  const WELCOME_MESSAGE = `Hi 👋 I'm Taras's AI assistant. Taras builds AI agents and automation that run in production.
Tell me what you want to automate, or ask about his projects and experience. To talk to Taras directly, book a call: ${BOOKING_URL}`;

  // Quick prompts: portfolio-focused only (hardening v2).
  const QUICK_PROMPTS = [
    'What can you build for my business?',
    'Do you have real client results?',
    'How much does a project cost?',
    'How do I book a call?',
  ];

  /* ---------- helpers ---------- */
  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (k === 'class') node.className = v;
        else if (k === 'dataset') Object.assign(node.dataset, v);
        else if (k.startsWith('on') && typeof v === 'function') {
          node.addEventListener(k.slice(2).toLowerCase(), v);
        } else if (k === 'html') {
          node.innerHTML = v;
        } else if (v === false || v == null) {
          /* skip */
        } else if (v === true) {
          node.setAttribute(k, '');
        } else {
          node.setAttribute(k, v);
        }
      }
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach((c) => {
        if (c == null) return;
        node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
      });
    }
    return node;
  }

  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(messages) {
    try {
      const trimmed = messages.slice(-40); // cap at 40
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (e) {
      /* quota or private mode — ignore */
    }
  }

  /* ---------- state ---------- */
  let isOpen = false;
  let isBusy = false;
  let history = loadHistory();
  let messagesEl, inputEl, sendBtn, panelEl, fabEl, quickEl, statusEl;

  /* ---------- mount ---------- */
  function mount() {
    // styles
    const style = el('style', { id: 'ai-assistant-styles' }, CSS);
    document.head.appendChild(style);

    const root = el('div', { id: 'ai-assistant-root' });
    document.body.appendChild(root);

    // FAB
    const fabIcon = el('svg', {
      width: 28,
      height: 28,
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '2',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'aria-hidden': 'true',
      html: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/><circle cx="9" cy="10" r="0.5" fill="currentColor"/><circle cx="13" cy="10" r="0.5" fill="currentColor"/><circle cx="17" cy="10" r="0.5" fill="currentColor"/>',
    });
    fabEl = el(
      'button',
      {
        class: 'ai-fab',
        type: 'button',
        'aria-label': 'Open AI Portfolio Assistant',
        'aria-expanded': 'false',
        'aria-controls': 'ai-assistant-panel',
        title: 'Chat with Taras\'s AI Assistant',
        onclick: toggleOpen,
      },
      fabIcon
    );
    const fabBadge = el('span', {
      class: 'ai-fab-badge',
      'aria-hidden': 'true',
      hidden: true,
    }, 'AI');
    fabEl.appendChild(fabBadge);
    root.appendChild(fabEl);

    // HI-4: "Chat with AI" label next to the fab on first visit.
    const fabLabel = el('div', {
      class: 'ai-fab-label',
      'aria-hidden': 'true',
    }, 'Chat with AI');
    root.appendChild(fabLabel);

    // Show on first visit (no localStorage flag), fade after 8s or on first interaction.
    if (!localStorage.getItem('taras-ai-fab-label-seen')) {
      setTimeout(() => {
        fabLabel.classList.add('visible');
        setTimeout(() => {
          fabLabel.classList.remove('visible');
          localStorage.setItem('taras-ai-fab-label-seen', '1');
        }, 8000);
      }, 1800);
      // Hide on any interaction with the fab
      fabEl.addEventListener('click', () => {
        fabLabel.classList.remove('visible');
        localStorage.setItem('taras-ai-fab-label-seen', '1');
      }, { once: true });
    }

    // Panel
    panelEl = el('div', {
      class: 'ai-panel',
      id: 'ai-assistant-panel',
      role: 'dialog',
      'aria-label': 'AI Portfolio Assistant',
      'aria-hidden': 'true',
    });

    // Header
    statusEl = el('p', { class: 'ai-header-status' }, 'Online · n8n workflow');
    const header = el('header', { class: 'ai-header' }, [
      el('div', { class: 'ai-header-avatar' }, 'AI'),
      el('div', { class: 'ai-header-meta' }, [
        el('h2', { class: 'ai-header-title' }, 'Taras\'s AI Assistant'),
        statusEl,
      ]),
      el('a', { class: 'ai-book', href: BOOKING_URL, target: '_blank', rel: 'noopener noreferrer' }, 'Book a call'),
      el(
        'button',
        {
          class: 'ai-close',
          type: 'button',
          'aria-label': 'Close AI assistant',
          onclick: closePanel,
          html: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
        }
      ),
    ]);
    panelEl.appendChild(header);

    // Messages
    messagesEl = el('div', {
      class: 'ai-messages',
      role: 'log',
      'aria-live': 'polite',
      'aria-relevant': 'additions',
      id: 'ai-messages',
    });
    panelEl.appendChild(messagesEl);

    // Quick prompts
    quickEl = el('div', { class: 'ai-quick', role: 'group', 'aria-label': 'Suggested questions' },
      QUICK_PROMPTS.map((q) =>
        el(
          'button',
          {
            class: 'ai-quick-btn',
            type: 'button',
            onclick: () => sendMessage(q),
          },
          q
        )
      )
    );
    panelEl.appendChild(quickEl);

    // Input
    inputEl = el('textarea', {
      class: 'ai-input',
      id: 'ai-input',
      rows: 1,
      placeholder: 'Describe your project or ask a question…',
      'aria-label': 'Message',
      onkeydown: handleInputKey,
      oninput: autosizeInput,
    });
    sendBtn = el(
      'button',
      {
        class: 'ai-send',
        type: 'button',
        'aria-label': 'Send message',
        onclick: () => sendMessage(inputEl.value),
        html: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>',
      }
    );
    panelEl.appendChild(
      el('div', { class: 'ai-input-row' }, [inputEl, sendBtn])
    );

    panelEl.appendChild(
      el('div', { class: 'ai-footer' }, [
        'Powered by ',
        el('a', { href: '#', onclick: (e) => { e.preventDefault(); openPanel(); } }, 'n8n workflow'),
        ' · ',
        el('a', { href: 'https://github.com/taras-polishchuk', target: '_blank', rel: 'noopener noreferrer' }, 'taras-polishchuk'),
      ])
    );

    root.appendChild(panelEl);

    // Initial render
    renderAll();
  }

  function renderAll() {
    messagesEl.innerHTML = '';
    if (history.length === 0) {
      // Single source of truth for initial chat state. The welcome message
      // is both rendered to the DOM AND saved to history, so subsequent
      // opens, refreshes, and state restorations all see exactly one entry.
      const welcomeMsg = { role: 'bot', text: WELCOME_MESSAGE, ts: Date.now() };
      history = [welcomeMsg];
      saveHistory(history);
      addMessage('bot', WELCOME_MESSAGE, { ts: welcomeMsg.ts, skipSave: true });
    } else {
      history.forEach((m) => addMessage(m.role, m.text, { ts: m.ts, skipSave: true }));
    }
    scrollToBottom();
  }

  // Render message text with clickable links (https URLs and emails) and
  // **bold**. DOM nodes only, never innerHTML: model output stays untrusted.
  function appendRichText(parent, text) {
    const re = /(https:\/\/[^\s<>"')]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\*\*[^*\n]+\*\*)/g;
    let last = 0;
    let m;
    const str = String(text == null ? '' : text);
    while ((m = re.exec(str)) !== null) {
      if (m.index > last) parent.appendChild(document.createTextNode(str.slice(last, m.index)));
      let tok = m[0];
      if (tok.startsWith('**')) {
        parent.appendChild(el('strong', null, tok.slice(2, -2)));
      } else {
        let tail = '';
        const tm = /[.,;:!?*]+$/.exec(tok);
        if (tm) { tail = tm[0]; tok = tok.slice(0, -tail.length); }
        const href = tok.startsWith('https://') ? tok : 'mailto:' + tok;
        parent.appendChild(el('a', { href: href, target: '_blank', rel: 'noopener noreferrer', class: 'ai-msg-link' }, tok));
        if (tail) parent.appendChild(document.createTextNode(tail));
      }
      last = m.index + m[0].length;
    }
    if (last < str.length) parent.appendChild(document.createTextNode(str.slice(last)));
  }

  function addMessage(role, text, opts) {
    opts = opts || {};
    const msg = el('div', { class: `ai-msg ai-msg-${role}`, role: 'article' });
    appendRichText(msg, text);
    if (opts.ts) {
      msg.appendChild(el('div', { class: 'ai-msg-meta' }, new Date(opts.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })));
    }
    messagesEl.appendChild(msg);
    if (!opts.skipSave) {
      scrollToBottom();
    }
    return msg;
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    });
  }

  function setStatus(state, text) {
    statusEl.dataset.state = state;
    statusEl.textContent = text;
  }

  /* ---------- panel toggle ---------- */
  function openPanel() {
    if (isOpen) return;
    isOpen = true;
    panelEl.dataset.open = 'true';
    panelEl.setAttribute('aria-hidden', 'false');
    fabEl.setAttribute('aria-expanded', 'true');
    setTimeout(() => inputEl.focus(), 50);
    // Note: the welcome message is injected (and saved to history) by
    // renderAll() during mount — never here. Injecting here would cause
    // a duplicate welcome on first open (RCA-2026-06-21 / decision.md #6).
  }

  function closePanel() {
    if (!isOpen) return;
    isOpen = false;
    panelEl.dataset.open = 'false';
    panelEl.setAttribute('aria-hidden', 'true');
    fabEl.setAttribute('aria-expanded', 'false');
  }

  function toggleOpen() {
    isOpen ? closePanel() : openPanel();
  }

  /* ---------- input ---------- */
  function handleInputKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputEl.value);
    }
  }

  /* Autosize the textarea: keep it at one line until the user pastes
     multi-line text or types a hard newline (Shift+Enter). Reset to
     one line on send. The CSS already sets overflow:hidden so there
     is no inner scrollbar at any height — this JS just keeps height
     in sync with content. Single-line height = line-height + padding
     (≈37px at 16px / 1.3 line-height / 8+8 padding). */
  function autosizeInput() {
    if (!inputEl) return;
    inputEl.style.height = 'auto';
    // Use scrollHeight which respects padding but ignores the hidden overflow.
    const next = Math.min(inputEl.scrollHeight, 120);
    inputEl.style.height = next + 'px';
  }

  /* ---------- send ---------- */
  async function sendMessage(text) {
    text = (text || '').trim();
    if (!text || isBusy) return;

    // --- Hardening v2: client-side guards (cost protection + abuse) ---

    // 1. Length cap
    if (text.length > MAX_INPUT) {
      const errText = `Your message is too long (${text.length} characters). Please keep it under ${MAX_INPUT} characters.`;
      addMessage('error', errText);
      history.push({ role: 'error', text: errText, ts: Date.now() });
      saveHistory(history);
      setStatus('error', 'Too long');
      return;
    }

    // 2. Max messages per session
    const msgCount = _getMsgCount();
    if (msgCount >= MAX_MESSAGES_PER_SESSION) {
      const errText = `You've reached the message limit for this session (${MAX_MESSAGES_PER_SESSION}). Start a new session by clearing site data to continue.`;
      addMessage('error', errText);
      history.push({ role: 'error', text: errText, ts: Date.now() });
      saveHistory(history);
      setStatus('error', 'Limit reached');
      return;
    }

    // 3. Rate limit
    const now = Date.now();
    const rate = _rateCheck(now);
    if (!rate.ok) {
      const secs = Math.ceil(rate.retryMs / 1000);
      const errText = `You're sending messages too quickly. Please wait ${secs} second${secs === 1 ? '' : 's'} before trying again.`;
      addMessage('error', errText);
      history.push({ role: 'error', text: errText, ts: Date.now() });
      saveHistory(history);
      setStatus('error', 'Slow down');
      return;
    }

    // --- Pass guards: proceed ---
    isBusy = true;
    inputEl.value = '';
    inputEl.style.height = 'auto'; // collapse back to single-line
    inputEl.disabled = true;
    sendBtn.disabled = true;

    addMessage('user', text);
    history.push({ role: 'user', text, ts: Date.now() });
    saveHistory(history);

    // Record rate + message count (after pass)
    _rateRecord(now, rate.log);
    _setMsgCount(msgCount + 1);

    // hide quick prompts after first user message
    if (!quickEl.hidden) quickEl.hidden = true;

    // typing indicator
    const typing = el(
      'div',
      { class: 'ai-typing', 'aria-label': 'Assistant is typing' },
      [el('span', { class: 'ai-typing-dot' }), el('span', { class: 'ai-typing-dot' }), el('span', { class: 'ai-typing-dot' })]
    );
    messagesEl.appendChild(typing);
    scrollToBottom();

    setStatus('thinking', 'Thinking…');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60_000);

    try {
      const res = await fetch(N8N_WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chatInput: text, sessionId: SESSION_ID }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      typing.remove();

      if (!res.ok) {
        const errText = `Sorry, the assistant is temporarily unavailable (HTTP ${res.status}). Please try again in a moment.`;
        addMessage('error', errText);
        history.push({ role: 'error', text: errText, ts: Date.now() });
        saveHistory(history);
        setStatus('error', `Error · HTTP ${res.status}`);
        return;
      }

      const data = await res.json();
      const reply = (data && (data.output || data.response || data.text)) || 'I have no answer for that right now.';
      addMessage('bot', reply);
      history.push({ role: 'bot', text: reply, ts: Date.now() });
      saveHistory(history);
      setStatus('online', 'Online · n8n workflow');
    } catch (err) {
      clearTimeout(timeoutId);
      typing.remove();
      const isAbort = err.name === 'AbortError';
      let errText;
      if (isAbort) {
        errText = 'Request timed out. The assistant took too long to respond. Please try again.';
      } else if (err && err.name === 'TypeError' && /fetch/i.test(err.message || '')) {
        // Most likely cause: Cloudflare Named Tunnel or n8n workflow down.
        // Surface a more helpful message than the generic "Network error".
        errText = 'Network error — the chat assistant is temporarily unavailable. Please retry; if it persists, the service may need attention.';
      } else {
        errText = 'Network error. Please check your connection and try again.';
      }
      addMessage('error', errText);
      history.push({ role: 'error', text: errText, ts: Date.now() });
      saveHistory(history);
      setStatus('error', isAbort ? 'Timeout' : 'Offline');
    } finally {
      isBusy = false;
      inputEl.disabled = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  /* ---------- boot ---------- */
  // Expose version for support / debugging.
  try { window.__aiWidget = { version: WIDGET_VERSION, sessionId: SESSION_ID }; } catch (e) {}

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }

  /* CTA hook: any element with [data-open-ai-chat] opens the panel */
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-open-ai-chat], #aiCtaOpen');
    if (t) {
      e.preventDefault();
      openPanel();
    }
  });
})();
