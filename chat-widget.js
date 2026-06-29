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
  const WIDGET_VERSION = '2.0.3';
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
  // The Cloudflare Quick Tunnel hostname is ephemeral and rotates on every
  // cloudflared restart. On a stale URL the fetch fails with a network
  // error and we surface a "Tunnel temporarily unavailable" status.
  // Recovery: re-run /home/taras/projects/ai/infrastructure/n8n/portfolio-agent-day0/scripts/recover-chat.sh
  const N8N_WEBHOOK_URL =
    'https://anna-formula-bracket-william.trycloudflare.com/webhook/0c620ad2-9b69-4484-a56f-5c1eddc47ead/chat';

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

  .ai-fab {
    position: fixed;
    right: 24px;
    bottom: 24px;
    z-index: 9998;
    width: 60px;
    height: 60px;
    border-radius: 9999px;
    background: linear-gradient(135deg, #7c6fff 0%, #4eecc8 100%);
    border: none;
    cursor: pointer;
    box-shadow: 0 8px 32px rgba(124, 111, 255, 0.35), 0 2px 8px rgba(0,0,0,0.4);
    transition: transform 180ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 180ms ease;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #0a0a0b;
    font-family: inherit;
  }
  .ai-fab:hover { transform: scale(1.07); box-shadow: 0 12px 40px rgba(124, 111, 255, 0.5); }
  .ai-fab:focus-visible { outline: 2px solid #4eecc8; outline-offset: 4px; }
  .ai-fab[aria-expanded="true"] { transform: rotate(90deg); }

  .ai-fab-badge {
    position: absolute;
    top: -2px;
    right: -2px;
    background: #4eecc8;
    color: #0a0a0b;
    font-size: 10px;
    font-weight: 700;
    line-height: 1;
    padding: 4px 6px;
    border-radius: 9999px;
    box-shadow: 0 0 0 2px #0a0a0b;
    pointer-events: none;
  }
  .ai-fab-badge[hidden] { display: none; }

  .ai-panel {
    position: fixed;
    right: 24px;
    bottom: 100px;
    z-index: 9999;
    width: min(380px, calc(100vw - 32px));
    height: min(620px, calc(100vh - 130px));
    background: #111113;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(124, 111, 255, 0.08);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    opacity: 0;
    transform: translateY(12px) scale(0.98);
    pointer-events: none;
    transition: opacity 180ms ease, transform 180ms cubic-bezier(0.16, 1, 0.3, 1);
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: #e8e8f0;
  }
  .ai-panel[data-open="true"] {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: auto;
  }

  .ai-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    background: linear-gradient(180deg, rgba(124, 111, 255, 0.08) 0%, rgba(124, 111, 255, 0) 100%);
  }
  .ai-header-avatar {
    width: 36px;
    height: 36px;
    border-radius: 9999px;
    background: linear-gradient(135deg, #7c6fff 0%, #4eecc8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    color: #0a0a0b;
    flex-shrink: 0;
  }
  .ai-header-meta { flex: 1; min-width: 0; }
  .ai-header-title {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.2;
    margin: 0;
  }
  .ai-header-status {
    font-size: 11px;
    color: #4eecc8;
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
    background: #4eecc8;
    box-shadow: 0 0 8px #4eecc8;
  }
  .ai-header-status[data-state="error"] { color: #ff6b6b; }
  .ai-header-status[data-state="error"]::before { background: #ff6b6b; box-shadow: 0 0 8px #ff6b6b; }
  .ai-close {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 8px;
    color: rgba(232, 232, 240, 0.6);
    transition: background 150ms, color 150ms;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .ai-close:hover { background: rgba(255, 255, 255, 0.06); color: #e8e8f0; }
  .ai-close:focus-visible { outline: 2px solid #7c6fff; outline-offset: 2px; }

  .ai-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
  }
  .ai-messages::-webkit-scrollbar { width: 6px; }
  .ai-messages::-webkit-scrollbar-track { background: transparent; }
  .ai-messages::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

  .ai-msg {
    max-width: 88%;
    padding: 10px 14px;
    border-radius: 14px;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
    animation: ai-msg-in 220ms cubic-bezier(0.16, 1, 0.3, 1);
  }
  @keyframes ai-msg-in {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .ai-msg-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #7c6fff 0%, #6a5fef 100%);
    color: #fff;
    border-bottom-right-radius: 4px;
  }

  .ai-msg-bot {
    align-self: flex-start;
    background: #1c1c21;
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: #e8e8f0;
    border-bottom-left-radius: 4px;
  }

  .ai-msg-error {
    align-self: flex-start;
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.25);
    color: #ff8a8a;
    border-bottom-left-radius: 4px;
    font-size: 13px;
  }

  .ai-msg-meta {
    font-size: 10px;
    color: rgba(232, 232, 240, 0.4);
    margin-top: 4px;
    text-align: right;
  }
  .ai-msg-bot .ai-msg-meta { text-align: left; }

  .ai-typing {
    align-self: flex-start;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    background: #1c1c21;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    border-bottom-left-radius: 4px;
  }
  .ai-typing-dot {
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: rgba(232, 232, 240, 0.4);
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
    background: rgba(124, 111, 255, 0.1);
    border: 1px solid rgba(124, 111, 255, 0.25);
    color: #c5beff;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 9999px;
    cursor: pointer;
    transition: background 150ms, border-color 150ms, color 150ms;
    font-family: inherit;
  }
  .ai-quick-btn:hover {
    background: rgba(124, 111, 255, 0.18);
    border-color: rgba(124, 111, 255, 0.4);
    color: #fff;
  }
  .ai-quick-btn:focus-visible { outline: 2px solid #4eecc8; outline-offset: 2px; }
  .ai-quick[hidden] { display: none; }

  .ai-input-row {
    display: flex;
    gap: 8px;
    padding: 12px 12px 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.07);
    background: #0e0e10;
  }
  .ai-input {
    flex: 1;
    min-width: 0;
    background: #16161a;
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #e8e8f0;
    /* font-size 16px is REQUIRED on iOS: WebKit auto-zooms the viewport
       on focus for any text input with computed font-size < 16px and
       does NOT reset the scale on blur, leaving the page stuck zoomed in.
       This MUST stay at 16px for any text input inside the panel. */
    font-size: 16px;
    font-family: inherit;
    padding: 8px 12px;
    border-radius: 12px;
    resize: none;
    /* Single-line visual: scroll only when user types Enter for newline.
       overflow-y: hidden kills the inner WebKit scrollbar; we manage
       line count in JS (autosizeInput) instead. max-height caps the
       textarea at ~5 lines if JS grows it. */
    overflow-y: hidden;
    overflow-x: hidden;
    max-height: 120px;
    line-height: 1.3;
    transition: border-color 150ms;
    /* Prevent inherited zoom on iOS Safari (iOS 16+). */
    -webkit-text-size-adjust: 100%;
    text-size-adjust: 100%;
  }
  /* Placeholder can stay smaller — it is NOT focused, so it does not
     trigger iOS auto-zoom. This frees horizontal space so the hint
     fits on one line in narrow mobile viewports. */
  .ai-input::placeholder {
    color: rgba(232, 232, 240, 0.4);
    font-size: 13px;
  }
  /* Belt-and-suspenders: kill any webkit scrollbar that could appear
     on the textarea itself (Safari sometimes shows a thin bar when
     content overflows before JS autosizes). */
  .ai-input::-webkit-scrollbar { width: 0; height: 0; display: none; }
  .ai-input { scrollbar-width: none; }
  .ai-input:focus {
    outline: none;
    border-color: #7c6fff;
  }
  .ai-input:disabled { opacity: 0.6; cursor: not-allowed; }

  .ai-send {
    background: linear-gradient(135deg, #7c6fff 0%, #4eecc8 100%);
    border: none;
    color: #0a0a0b;
    font-weight: 600;
    padding: 0 14px;
    border-radius: 12px;
    cursor: pointer;
    font-size: 13px;
    transition: transform 150ms, opacity 150ms;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .ai-send:hover:not(:disabled) { transform: scale(1.04); }
  .ai-send:disabled { opacity: 0.4; cursor: not-allowed; }
  .ai-send:focus-visible { outline: 2px solid #4eecc8; outline-offset: 2px; }
  .ai-send svg { width: 16px; height: 16px; }

  .ai-footer {
    text-align: center;
    font-size: 10px;
    color: rgba(232, 232, 240, 0.3);
    padding: 6px;
    background: #0e0e10;
  }
  .ai-footer a { color: rgba(124, 111, 255, 0.6); text-decoration: none; }
  .ai-footer a:hover { color: #7c6fff; }

  @media (max-width: 480px) {
    .ai-panel {
      right: 0;
      bottom: 0;
      width: 100vw;
      height: 100dvh;
      max-height: 100dvh;
      border-radius: 0;
      border: none;
    }
    .ai-fab[data-mobile="true"] { display: none; }
  }
  `;

  // Welcome: portfolio-only topics, no company/Shopify mention (hardening v2).
  const WELCOME_MESSAGE = `Hi 👋 I'm Taras's AI Portfolio Assistant. Ask me about:
• AI automation projects
• n8n workflows
• Hermes platform
• technical stack
• engineering experience`;

  // Quick prompts: portfolio-focused only (hardening v2).
  const QUICK_PROMPTS = [
    'What AI systems have you built?',
    'How do you use n8n?',
    'What is Hermes?',
    'What is your strongest project?',
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
      placeholder: 'Ask about projects, stack, experience…',
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

  function addMessage(role, text, opts) {
    opts = opts || {};
    const msg = el('div', { class: `ai-msg ai-msg-${role}`, role: 'article' });
    msg.appendChild(document.createTextNode(text));
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
        // Most likely cause: Cloudflare Quick Tunnel hostname rotated and
        // the hard-coded URL no longer resolves. Surface a more helpful
        // message than the generic "Network error".
        errText = 'Network error — the public tunnel is temporarily unavailable. Please retry in a few minutes; if it persists, the assistant URL needs a refresh.';
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
