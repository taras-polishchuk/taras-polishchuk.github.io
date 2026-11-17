/* Sound design: ambient Ab-minor pad, hover/click/open/close SFX, scroll warp. Opt-in via #audioToggle. Ported from portfolio v1 (2026-08). */
(function initAudio() {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;

  let ac = null, master = null;
  let ambiStarted = false, enabled = false;

  function boot() {
    if (ac) { if (ac.state === 'suspended') ac.resume(); return; }
    ac = new AC();
    master = ac.createGain();
    master.gain.value = 0;
    master.connect(ac.destination);
  }

  // ── Ambient pad — Ab minor chord, procedural convolver reverb ──
  function startAmbient() {
    if (ambiStarted) return;
    ambiStarted = true;
    const now = ac.currentTime;

    const convolver = ac.createConvolver();
    const irLen = ac.sampleRate * 3.5;
    const ir = ac.createBuffer(2, irLen, ac.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = ir.getChannelData(c);
      for (let i = 0; i < irLen; i++)
        d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / irLen, 2.2);
    }
    convolver.buffer = ir;

    const wetGain = ac.createGain(); wetGain.gain.value = 0.45;
    convolver.connect(wetGain); wetGain.connect(master);

    const lpf = ac.createBiquadFilter();
    lpf.type = 'lowpass'; lpf.frequency.value = 700; lpf.Q.value = 0.4;
    lpf.connect(convolver);

    const dryOut = ac.createGain(); dryOut.gain.value = 0.55;
    dryOut.connect(master);

    const ambiOut = ac.createGain(); ambiOut.gain.value = 0.13;
    ambiOut.connect(lpf); ambiOut.connect(dryOut);

    // Ab Cb Eb across 3 octaves
    const notes = [
      { f: 51.9,  t: 'sine',     g: 0.55 },
      { f: 61.7,  t: 'sine',     g: 0.30 },
      { f: 77.8,  t: 'sine',     g: 0.28 },
      { f: 103.8, t: 'sine',     g: 0.42 },
      { f: 123.5, t: 'triangle', g: 0.18 },
      { f: 155.6, t: 'sine',     g: 0.20 },
      { f: 207.7, t: 'sine',     g: 0.14 },
      { f: 247.0, t: 'triangle', g: 0.07 },
    ];

    notes.forEach(({ f, t, g }, i) => {
      const osc = ac.createOscillator(), gain = ac.createGain();
      const lfo = ac.createOscillator(), lfoGain = ac.createGain();
      const aLfo = ac.createOscillator(), aGain = ac.createGain();

      osc.type = t; osc.frequency.value = f;

      lfo.frequency.value = 0.06 + i * 0.025; lfoGain.gain.value = 0.12;
      lfo.connect(lfoGain); lfoGain.connect(osc.frequency);

      aLfo.frequency.value = 0.04 + i * 0.018; aGain.gain.value = g * 0.28;
      aLfo.connect(aGain); aGain.connect(gain.gain);

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(g, now + 4 + i * 1.4);
      osc.connect(gain); gain.connect(ambiOut);
      osc.start(now); lfo.start(now); aLfo.start(now);
    });
  }

  // ── SFX helpers ───────────────────────────────────────
  function sTone(freq, type, dur, vol, freqEnd) {
    if (!enabled || !ac) return;
    const t = ac.currentTime;
    const osc = ac.createOscillator(), g = ac.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    if (freqEnd) osc.frequency.exponentialRampToValueAtTime(freqEnd, t + dur);
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(vol, t + 0.004);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(g); g.connect(master);
    osc.start(); osc.stop(t + dur + 0.015);
  }

  function sNoise(dur, vol, f1, f2, filterType) {
    if (!enabled || !ac) return;
    const t = ac.currentTime, sr = ac.sampleRate;
    const buf = ac.createBuffer(1, sr * dur, sr);
    const d = buf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const src = ac.createBufferSource(); src.buffer = buf;
    const flt = ac.createBiquadFilter();
    flt.type = filterType;
    flt.frequency.setValueAtTime(f1, t);
    flt.frequency.exponentialRampToValueAtTime(f2, t + dur);
    flt.Q.value = 1.5;
    const g = ac.createGain();
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    src.connect(flt); flt.connect(g); g.connect(master);
    src.start(); src.stop(t + dur);
  }

  const sfx = {
    hover()  { sTone(1800, 'sine', 0.07, 0.022, 2400); },
    click()  { sTone(2000, 'sine', 0.10, 0.055, 700); sTone(900, 'triangle', 0.05, 0.025); },
    open()   { sNoise(0.65, 0.07, 400, 2800, 'bandpass'); sTone(110, 'sine', 1.1, 0.045, 220); },
    close()  { sNoise(0.50, 0.06, 2400, 300, 'bandpass'); sTone(440, 'sine', 0.55, 0.04, 110); },
  };

  // ── Toggle button ────────────────────────────────────────
  const ICON_ON  = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19.5 5a10 10 0 0 1 0 14"/></svg>`;
  const ICON_OFF = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="22" y1="9" x2="16" y2="15"/><line x1="16" y1="9" x2="22" y2="15"/></svg>`;

  const btn = document.createElement('button');
  btn.id = 'audioToggle';
  btn.setAttribute('aria-label', 'Toggle ambient audio');
  btn.title = 'Ambient audio';
  btn.innerHTML = ICON_OFF;
  document.body.appendChild(btn);

  // ── Audio hint toast — HI-7: opt-in only. Hint no longer auto-shows on
  //     first load; it appears only when the user clicks the audio toggle.
  const hintEl = document.getElementById('audioHint');
  const hintDismiss = hintEl && hintEl.querySelector('.audio-hint-dismiss');
  let hintTimer = null;

  function hideHint() {
    if (!hintEl) return;
    clearTimeout(hintTimer);
    hintEl.classList.add('hiding');
    setTimeout(() => { hintEl.classList.remove('visible', 'hiding'); }, 460);
  }

  // Expose a global so the audio-toggle button can trigger the hint on demand.
  window.__showAudioHint = function () {
    if (!hintEl) return;
    hintEl.classList.add('visible');
    clearTimeout(hintTimer);
    hintTimer = setTimeout(hideHint, 8000);
  };

  if (hintDismiss) {
    hintDismiss.addEventListener('click', () => {
      localStorage.setItem('audioHintDismissed', '1');
      hideHint();
    });
  }

  // Show the hint once, 4 s after load, unless dismissed before. Auto-hide after 8 s.
  if (hintEl && !localStorage.getItem('audioHintDismissed') && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    setTimeout(() => {
      if (enabled) return;
      hintEl.classList.add('visible');
      setTimeout(() => { if (hintEl.classList.contains('visible')) hideHint(); }, 8000);
    }, 4000);
  }

  const cRing = document.getElementById('cursorRing');
  btn.addEventListener('mouseenter', () => cRing && cRing.classList.add('hover'));
  btn.addEventListener('mouseleave', () => cRing && cRing.classList.remove('hover'));

  btn.addEventListener('click', () => {
    // Dismiss hint when user interacts with audio toggle
    if (hintEl && hintEl.classList.contains('visible')) {
      localStorage.setItem('audioHintDismissed', '1');
      hideHint();
    }
    boot();
    if (enabled) {
      enabled = false;
      master.gain.setTargetAtTime(0, ac.currentTime, 0.5);
      btn.innerHTML = ICON_OFF;
      btn.classList.remove('active');
    } else {
      enabled = true;
      startAmbient();
      master.gain.setTargetAtTime(1, ac.currentTime, 2.0);
      btn.innerHTML = ICON_ON;
      btn.classList.add('active');
    }
  });

  // ── Hook SFX to page interactions ───────────────────────────
  document.addEventListener('mousedown', e => {
    if (!enabled) return;
    if (e.target.closest('a, button, [role="button"]')) sfx.click();
  }, true);

  document.querySelectorAll('a, button, [role="button"], .social-icon').forEach(el => {
    el.addEventListener('mouseenter', () => { if (enabled) sfx.hover(); });
  });

  // Overlay open / close via MutationObserver
  let overlayWasActive = false;
  const overlayEl = document.getElementById('projects-overlay');
  if (overlayEl) {
    new MutationObserver(() => {
      const isActive = overlayEl.classList.contains('active');
      if (isActive  && !overlayWasActive) { if (enabled) sfx.open();  }
      if (!isActive && overlayWasActive)  { if (enabled) sfx.close(); }
      overlayWasActive = isActive;
    }).observe(overlayEl, { attributes: true, attributeFilter: ['class'] });
  }

  // Add hover SFX to project cards when grid is populated
  const gridEl = document.getElementById('projectsGrid');
  if (gridEl) {
    new MutationObserver(() => {
      gridEl.querySelectorAll('.project-card').forEach(el => {
        el.addEventListener('mouseenter', () => { if (enabled) sfx.hover(); });
      });
    }).observe(gridEl, { childList: true });
  }

  // ── Mouse thruster — space shuttle flying through space ────────────────
  let thrNodes = null, thrFadeTimer = null;
  let lastMX = 0, lastMY = 0, lastMT = 0;

  function ensureThruster() {
    if (thrNodes || !ac) return;
    // Engine: two sine oscillators — thin, airy, no harsh sawtooth harmonics
    const osc1 = ac.createOscillator(), osc2 = ac.createOscillator();
    osc1.type = 'sine'; osc1.frequency.value = 180;
    osc2.type = 'sine'; osc2.frequency.value = 183.5; // subtle beating

    // Thrust hiss: narrow high-pitched bandpass — more "air" than "roar"
    const nBuf = ac.createBuffer(1, ac.sampleRate * 3, ac.sampleRate);
    const nd = nBuf.getChannelData(0);
    for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
    const nSrc = ac.createBufferSource(); nSrc.buffer = nBuf; nSrc.loop = true;
    const nFlt = ac.createBiquadFilter(); nFlt.type = 'bandpass'; nFlt.frequency.value = 900; nFlt.Q.value = 2.5;
    const nGain = ac.createGain(); nGain.gain.value = 0.35;

    // HP to cut low rumble, keep it airy
    const hpf = ac.createBiquadFilter(); hpf.type = 'highpass'; hpf.frequency.value = 160;
    const thrGain = ac.createGain(); thrGain.gain.value = 0;

    osc1.connect(hpf); osc2.connect(hpf);
    nSrc.connect(nFlt); nFlt.connect(nGain); nGain.connect(hpf);
    hpf.connect(thrGain); thrGain.connect(master);

    osc1.start(); osc2.start(); nSrc.start();
    thrNodes = { osc1, osc2, nFlt, hpf, thrGain };
  }

  document.addEventListener('mousemove', e => {
    if (!enabled) return;
    const now = performance.now();
    const dx = e.clientX - lastMX, dy = e.clientY - lastMY;
    const dt = Math.max(now - lastMT, 1);
    const speed = Math.sqrt(dx * dx + dy * dy) / dt; // px/ms
    lastMX = e.clientX; lastMY = e.clientY; lastMT = now;

    ensureThruster();
    const t = ac.currentTime;
    const spd = Math.min(speed / 1.6, 1); // normalize 0–1

    // Pitch drifts up gently with speed: 180 → 260 Hz
    thrNodes.osc1.frequency.setTargetAtTime(180 + spd * 80,  t, 0.12);
    thrNodes.osc2.frequency.setTargetAtTime(183.5 + spd * 84, t, 0.12);

    // Hiss shifts up from 900 → 1600 Hz — barely noticeable but present
    thrNodes.nFlt.frequency.setTargetAtTime(900 + spd * 700, t, 0.14);

    // Volume: max 0.024 — about half of before, still audible
    thrNodes.thrGain.gain.setTargetAtTime(spd * 0.024, t, 0.08);

    // Space-dust micro-bursts at high speed
    if (spd > 0.55 && Math.random() < 0.07) {
      sNoise(0.22, 0.015 * spd, 1400 + spd * 1600, 280, 'bandpass');
    }

    // Fade engine out 200ms after last movement
    clearTimeout(thrFadeTimer);
    thrFadeTimer = setTimeout(() => {
      if (thrNodes) thrNodes.thrGain.gain.setTargetAtTime(0, ac.currentTime, 0.28);
    }, 200);
  });

  // ── Scroll warp — gentle space-warp whoosh on scroll ──────────────────
  let scrollFadeTimer = null, lastScrollY = window.scrollY, lastScrollT = 0;
  let touchStartY = 0;

  function scrollWarp(delta, speed) {
    if (!enabled || !ac) return;
    const t = ac.currentTime;
    const dir = delta > 0 ? 1 : -1; // 1=down, -1=up
    const intensity = Math.min(Math.abs(speed) / 2.5, 1); // normalize

    // Sine sweep: down=descending pitch, up=ascending (Doppler-like)
    const freqStart = dir > 0 ? 520 + intensity * 280 : 280 + intensity * 140;
    const freqEnd   = dir > 0 ? freqStart * 0.55       : freqStart * 1.75;
    const dur = 0.32 + intensity * 0.22;

    const osc = ac.createOscillator(), g = ac.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(freqStart, t);
    osc.frequency.exponentialRampToValueAtTime(freqEnd, t + dur);

    // Soft attack + quick fade — very unobtrusive
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.028 + intensity * 0.022, t + 0.018);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);

    // Narrow bandpass gives it ethereal quality
    const bpf = ac.createBiquadFilter(); bpf.type = 'bandpass';
    bpf.frequency.setValueAtTime(freqStart, t);
    bpf.frequency.exponentialRampToValueAtTime(freqEnd, t + dur);
    bpf.Q.value = 3.5;

    osc.connect(bpf); bpf.connect(g); g.connect(master);
    osc.start(t); osc.stop(t + dur + 0.02);

    // Faint stardust shimmer on fast scroll
    if (intensity > 0.5 && Math.random() < 0.4) {
      sTone(2200 + Math.random() * 800, 'sine', 0.18, 0.008 * intensity, 3800 + Math.random() * 600);
    }
  }

  // Wheel (mouse + trackpad)
  let wheelAcc = 0, wheelTimer = null;
  document.addEventListener('wheel', e => {
    if (!enabled) return;
    const now = performance.now();
    wheelAcc += e.deltaY;
    clearTimeout(wheelTimer);
    wheelTimer = setTimeout(() => {
      const dt = Math.max(now - lastScrollT, 1);
      const speed = Math.abs(wheelAcc) / dt;
      scrollWarp(wheelAcc, speed);
      lastScrollT = now;
      wheelAcc = 0;
    }, 60);
  }, { passive: true });

  // Touch scroll (mobile)
  document.addEventListener('touchstart', e => {
    touchStartY = e.touches[0].clientY;
    lastScrollT = performance.now();
  }, { passive: true });

  document.addEventListener('touchend', e => {
    if (!enabled) return;
    const delta = touchStartY - (e.changedTouches[0].clientY);
    const dt = Math.max(performance.now() - lastScrollT, 1);
    if (Math.abs(delta) < 8) return; // ignore micro-swipes
    scrollWarp(delta, Math.abs(delta) / dt);
  }, { passive: true });
})();
