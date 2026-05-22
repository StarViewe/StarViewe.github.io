---
title: Music Player Prototype
date: 2026-05-22 14:30:00
---

<!-- Prototype question: what should a lightweight browser-based music player feel like in this blog project? Three variants are switchable via ?variant=. -->

<div id="music-player-prototype-app"></div>

<style>
  :root {
    color-scheme: dark;
    --bg: #08111f;
    --panel: rgba(10, 23, 42, 0.78);
    --panel-strong: rgba(14, 30, 52, 0.94);
    --line: rgba(255, 255, 255, 0.1);
    --text: #eef4ff;
    --muted: #92a7c6;
    --accent: #ff7a18;
    --accent-2: #ffbc42;
    --accent-3: #3dd6d0;
    --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
  }

  .music-prototype {
    position: relative;
    margin: 32px auto 96px;
    max-width: 1100px;
    min-height: 760px;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 32px;
    background:
      radial-gradient(circle at top left, rgba(61, 214, 208, 0.18), transparent 28%),
      radial-gradient(circle at top right, rgba(255, 122, 24, 0.2), transparent 26%),
      linear-gradient(145deg, #07111e 0%, #0c1b31 44%, #10213f 100%);
    box-shadow: var(--shadow);
    color: var(--text);
  }

  .music-prototype * {
    box-sizing: border-box;
  }

  .music-prototype button,
  .music-prototype input {
    font: inherit;
  }

  .music-prototype button {
    border: 0;
    color: inherit;
    cursor: pointer;
  }

  .music-prototype-shell {
    position: relative;
    z-index: 1;
    padding: 40px;
  }

  .music-prototype-kicker {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding: 8px 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    color: #d8e6ff;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  .music-prototype-title {
    margin: 0;
    font-size: clamp(34px, 5vw, 62px);
    line-height: 0.95;
    letter-spacing: -0.04em;
  }

  .music-prototype-subtitle {
    max-width: 620px;
    margin: 14px 0 0;
    color: var(--muted);
    font-size: 16px;
    line-height: 1.7;
  }

  .music-grid {
    display: grid;
    gap: 24px;
    margin-top: 34px;
  }

  .music-grid.variant-a {
    grid-template-columns: 1.3fr 0.9fr;
  }

  .music-grid.variant-b {
    grid-template-columns: 0.8fr 1.2fr;
  }

  .music-grid.variant-c {
    grid-template-columns: 1fr;
  }

  .panel {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 28px;
    background: var(--panel);
    backdrop-filter: blur(20px);
  }

  .panel-inner {
    padding: 28px;
  }

  .hero-player {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 28px;
    align-items: center;
  }

  .cover-stack {
    position: relative;
    width: 220px;
    height: 220px;
    margin: 0 auto;
  }

  .cover-stack::before,
  .cover-stack::after {
    content: "";
    position: absolute;
    inset: 14px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0));
    transform: rotate(-8deg);
    opacity: 0.45;
  }

  .cover-stack::after {
    inset: 22px;
    transform: rotate(8deg);
    opacity: 0.28;
  }

  .cover {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 24px;
    border-radius: 32px;
    background: linear-gradient(145deg, var(--cover-a), var(--cover-b));
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.16), 0 18px 40px rgba(0,0,0,0.28);
  }

  .cover-small {
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.72);
  }

  .cover-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.16);
    font-size: 12px;
  }

  .pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: #fff;
    box-shadow: 0 0 0 0 rgba(255,255,255,0.5);
    animation: pulse-dot 1.8s infinite;
  }

  @keyframes pulse-dot {
    0% { box-shadow: 0 0 0 0 rgba(255,255,255,0.45); }
    70% { box-shadow: 0 0 0 12px rgba(255,255,255,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); }
  }

  .track-meta {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .track-caption {
    color: var(--muted);
    font-size: 13px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  .track-title {
    margin: 0;
    font-size: clamp(28px, 4vw, 42px);
    line-height: 1;
    letter-spacing: -0.04em;
  }

  .track-desc {
    margin: 0;
    color: var(--muted);
    line-height: 1.7;
  }

  .pill-row,
  .control-row,
  .stat-row,
  .playlist,
  .wave-bars,
  .compact-head,
  .dial-row,
  .vinyl-stage,
  .timeline-card,
  .side-list,
  .proto-notes {
    display: flex;
    gap: 12px;
  }

  .pill-row {
    flex-wrap: wrap;
  }

  .pill {
    padding: 10px 14px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    background: rgba(255,255,255,0.05);
    color: #d9e8ff;
    font-size: 13px;
  }

  .control-row {
    align-items: center;
    margin-top: 14px;
  }

  .icon-btn,
  .primary-btn,
  .ghost-btn,
  .playlist-item {
    transition: transform 140ms ease, background 140ms ease, border-color 140ms ease;
  }

  .icon-btn:hover,
  .primary-btn:hover,
  .ghost-btn:hover,
  .playlist-item:hover {
    transform: translateY(-1px);
  }

  .icon-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    background: rgba(255,255,255,0.06);
  }

  .primary-btn {
    padding: 0 24px;
    height: 56px;
    border-radius: 18px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #16120d;
    font-weight: 700;
  }

  .ghost-btn {
    padding: 0 18px;
    height: 56px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    background: rgba(255,255,255,0.05);
  }

  .timeline {
    margin-top: 20px;
  }

  .timeline-labels {
    display: flex;
    justify-content: space-between;
    color: var(--muted);
    font-size: 13px;
  }

  .timeline input[type="range"],
  .volume-control input[type="range"] {
    width: 100%;
    margin: 12px 0 6px;
    accent-color: var(--accent-2);
  }

  .stat-row {
    flex-wrap: wrap;
    margin-top: 24px;
  }

  .stat-card {
    flex: 1 1 140px;
    padding: 18px 18px 16px;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    background: rgba(255,255,255,0.04);
  }

  .stat-card strong {
    display: block;
    margin-bottom: 8px;
    font-size: 24px;
    letter-spacing: -0.04em;
  }

  .stat-card span {
    color: var(--muted);
    font-size: 13px;
  }

  .playlist {
    flex-direction: column;
  }

  .playlist-item {
    display: grid;
    grid-template-columns: 56px 1fr auto;
    gap: 14px;
    align-items: center;
    padding: 14px;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    background: rgba(255,255,255,0.04);
    text-align: left;
  }

  .playlist-item.is-active {
    border-color: rgba(255, 188, 66, 0.48);
    background: rgba(255, 188, 66, 0.12);
  }

  .playlist-thumb {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: linear-gradient(135deg, var(--cover-a), var(--cover-b));
  }

  .playlist-item strong,
  .side-item strong {
    display: block;
    margin-bottom: 4px;
    font-size: 15px;
  }

  .playlist-item span,
  .side-item span,
  .mini-note,
  .proto-notes li {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.6;
  }

  .playlist-length {
    color: var(--muted);
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .variant-b-shell {
    display: grid;
    grid-template-columns: 260px 1fr;
    min-height: 620px;
  }

  .variant-b-sidebar {
    padding: 28px 22px;
    border-right: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04);
  }

  .compact-head {
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }

  .compact-logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--accent-3), #5b7cff);
    color: #06101f;
    font-weight: 800;
  }

  .side-list {
    flex-direction: column;
  }

  .side-item {
    padding: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    background: rgba(255,255,255,0.04);
    cursor: pointer;
  }

  .side-item.is-active {
    border-color: rgba(61,214,208,0.48);
    background: rgba(61,214,208,0.12);
  }

  .variant-b-main {
    padding: 28px;
  }

  .vinyl-stage {
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-bottom: 24px;
  }

  .vinyl-disc {
    position: relative;
    width: 230px;
    height: 230px;
    border-radius: 999px;
    background:
      radial-gradient(circle at center, #0c1727 0 14px, #d7e3ff 14px 28px, #0f1f38 28px 34px, transparent 34px),
      repeating-radial-gradient(circle at center, #08111d 0 8px, #111f34 8px 14px, #08111d 14px 20px);
    border: 10px solid rgba(255,255,255,0.08);
    box-shadow: inset 0 0 24px rgba(255,255,255,0.05), 0 20px 40px rgba(0,0,0,0.28);
  }

  .vinyl-disc.is-playing {
    animation: spin-disc 8s linear infinite;
  }

  @keyframes spin-disc {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .wave-panel {
    display: grid;
    gap: 18px;
    margin-top: 16px;
  }

  .wave-bars {
    align-items: flex-end;
    height: 110px;
  }

  .wave-bars span {
    flex: 1;
    border-radius: 999px 999px 0 0;
    background: linear-gradient(180deg, var(--accent-3), rgba(61,214,208,0.18));
    min-width: 10px;
    height: 18px;
    transform-origin: bottom center;
    animation: wave-idle 1.4s ease-in-out infinite;
  }

  .wave-bars.is-playing span:nth-child(1) { animation-delay: 0.0s; }
  .wave-bars.is-playing span:nth-child(2) { animation-delay: 0.1s; }
  .wave-bars.is-playing span:nth-child(3) { animation-delay: 0.2s; }
  .wave-bars.is-playing span:nth-child(4) { animation-delay: 0.3s; }
  .wave-bars.is-playing span:nth-child(5) { animation-delay: 0.4s; }
  .wave-bars.is-playing span:nth-child(6) { animation-delay: 0.5s; }
  .wave-bars.is-playing span:nth-child(7) { animation-delay: 0.6s; }
  .wave-bars.is-playing span:nth-child(8) { animation-delay: 0.7s; }
  .wave-bars.is-playing span:nth-child(9) { animation-delay: 0.8s; }

  @keyframes wave-idle {
    0%, 100% { height: 18px; opacity: 0.45; }
    50% { height: 78px; opacity: 1; }
  }

  .dial-row {
    flex-wrap: wrap;
    margin-top: 12px;
  }

  .dial-card {
    flex: 1 1 140px;
    padding: 16px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04);
  }

  .dial-card strong {
    display: block;
    font-size: 24px;
    margin-bottom: 4px;
  }

  .variant-c-head {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: flex-end;
    flex-wrap: wrap;
  }

  .timeline-board {
    display: grid;
    gap: 18px;
    margin-top: 28px;
  }

  .timeline-card {
    align-items: stretch;
    gap: 18px;
  }

  .timeline-index {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 58px;
    border-radius: 18px;
    background: rgba(255,255,255,0.06);
    font-size: 22px;
    font-weight: 700;
    color: rgba(255,255,255,0.84);
  }

  .timeline-content {
    flex: 1;
  }

  .timeline-content-top {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }

  .timeline-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }

  .timeline-badge {
    padding: 7px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    color: #dbe8ff;
    font-size: 12px;
  }

  .volume-control {
    margin-top: 4px;
  }

  .proto-state {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 12px;
    margin-top: 24px;
  }

  .proto-state div {
    padding: 14px 16px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.04);
  }

  .proto-state strong {
    display: block;
    margin-bottom: 6px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
  }

  .proto-state span {
    font-size: 16px;
  }

  .prototype-switcher {
    position: fixed;
    left: 50%;
    bottom: 18px;
    z-index: 99;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 999px;
    background: rgba(7, 13, 23, 0.92);
    backdrop-filter: blur(16px);
    box-shadow: 0 14px 40px rgba(0,0,0,0.36);
    transform: translateX(-50%);
  }

  .switcher-btn {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
  }

  .switcher-label {
    min-width: 172px;
    color: #f2f6ff;
    text-align: center;
    font-size: 13px;
    line-height: 1.35;
  }

  .switcher-label span {
    display: block;
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .proto-notes {
    flex-direction: column;
    margin-top: 22px;
    padding-left: 18px;
  }

  @media (max-width: 900px) {
    .music-grid.variant-a,
    .music-grid.variant-b,
    .variant-b-shell,
    .hero-player {
      grid-template-columns: 1fr;
    }

    .cover-stack,
    .vinyl-disc {
      margin: 0 auto;
    }

    .music-prototype-shell {
      padding: 24px;
    }

    .music-prototype {
      min-height: auto;
      border-radius: 24px;
    }
  }
</style>

<script>
  (() => {
    const mount = document.getElementById('music-player-prototype-app');
    if (!mount) return;

    const tracks = [
      {
        id: 't1',
        title: 'Neon Drift',
        artist: 'StarViewe FM',
        length: 133,
        bpm: 104,
        colorA: '#ff7a18',
        colorB: '#ff3c7d',
        mood: 'Night drive',
        note: 'soft bass + warm lead',
        desc: 'A warm synth loop for late-night focus sessions.',
        bars: [28, 42, 36, 68, 54, 74, 48, 64, 38],
        pattern: [
          { f: 220, d: 0.36 }, { f: 277.18, d: 0.24 }, { f: 329.63, d: 0.24 },
          { f: 277.18, d: 0.36 }, { f: 246.94, d: 0.24 }, { f: 220, d: 0.56 }
        ]
      },
      {
        id: 't2',
        title: 'Harbor Echo',
        artist: 'Blue Pier Unit',
        length: 168,
        bpm: 92,
        colorA: '#3dd6d0',
        colorB: '#376bff',
        mood: 'Sea breeze',
        note: 'glass plucks + tape hiss',
        desc: 'A cleaner, slower loop with space between notes.',
        bars: [24, 56, 32, 44, 66, 30, 58, 34, 62],
        pattern: [
          { f: 196, d: 0.45 }, { f: 246.94, d: 0.25 }, { f: 293.66, d: 0.25 },
          { f: 392, d: 0.35 }, { f: 293.66, d: 0.25 }, { f: 246.94, d: 0.45 }
        ]
      },
      {
        id: 't3',
        title: 'Velvet Static',
        artist: 'Low Power Club',
        length: 151,
        bpm: 118,
        colorA: '#ffbc42',
        colorB: '#fb5e56',
        mood: 'Retro pulse',
        note: 'tight kick + chopped arps',
        desc: 'A punchier loop for a brighter, more kinetic player feel.',
        bars: [44, 62, 76, 38, 58, 82, 48, 70, 52],
        pattern: [
          { f: 246.94, d: 0.18 }, { f: 329.63, d: 0.18 }, { f: 392, d: 0.18 },
          { f: 493.88, d: 0.18 }, { f: 392, d: 0.18 }, { f: 329.63, d: 0.36 }
        ]
      }
    ];

    const variants = [
      { key: 'A', name: 'Cinematic Cover' },
      { key: 'B', name: 'Studio Rack' },
      { key: 'C', name: 'Timeline Queue' }
    ];

    const url = new URL(window.location.href);
    const variantKeys = variants.map((item) => item.key);
    const initialVariant = variantKeys.includes((url.searchParams.get('variant') || '').toUpperCase())
      ? url.searchParams.get('variant').toUpperCase()
      : 'A';

    const state = {
      variant: initialVariant,
      trackIndex: 0,
      isPlaying: false,
      currentTime: 0,
      volume: 72,
      loop: true,
      timerId: null,
      audioContext: null,
      nextNoteAt: 0,
      noteIndex: 0,
      lookAheadId: null,
      voices: []
    };

    const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

    function getTrack() {
      return tracks[state.trackIndex];
    }

    function formatTime(totalSeconds) {
      const safe = Math.max(0, Math.floor(totalSeconds));
      const min = Math.floor(safe / 60);
      const sec = safe % 60;
      return `${min}:${String(sec).padStart(2, '0')}`;
    }

    function updateUrlVariant() {
      const nextUrl = new URL(window.location.href);
      nextUrl.searchParams.set('variant', state.variant);
      window.history.replaceState({}, '', nextUrl.toString());
    }

    function ensureAudioContext() {
      if (!state.audioContext) {
        const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextCtor) return null;
        state.audioContext = new AudioContextCtor();
      }
      if (state.audioContext.state === 'suspended') {
        state.audioContext.resume().catch(() => {});
      }
      return state.audioContext;
    }

    function clearVoices() {
      state.voices.forEach((voice) => {
        try { voice.osc.stop(); } catch (error) {}
        try { voice.osc.disconnect(); } catch (error) {}
        try { voice.gain.disconnect(); } catch (error) {}
      });
      state.voices = [];
    }

    function stopScheduler() {
      if (state.lookAheadId) {
        window.clearTimeout(state.lookAheadId);
        state.lookAheadId = null;
      }
      clearVoices();
    }

    function playTone(freq, startAt, duration) {
      const ctx = ensureAudioContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const wobble = ctx.createOscillator();
      const wobbleGain = ctx.createGain();

      osc.type = state.trackIndex === 1 ? 'triangle' : state.trackIndex === 2 ? 'square' : 'sine';
      osc.frequency.setValueAtTime(freq, startAt);

      wobble.type = 'sine';
      wobble.frequency.setValueAtTime(4.4, startAt);
      wobbleGain.gain.setValueAtTime(4, startAt);

      gain.gain.setValueAtTime(0.0001, startAt);
      gain.gain.linearRampToValueAtTime(0.12 * (state.volume / 100), startAt + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);

      wobble.connect(wobbleGain);
      wobbleGain.connect(osc.frequency);
      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(startAt);
      wobble.start(startAt);
      osc.stop(startAt + duration + 0.05);
      wobble.stop(startAt + duration + 0.05);

      state.voices.push({ osc, gain });
    }

    function scheduleNotes() {
      if (!state.isPlaying) return;
      const ctx = ensureAudioContext();
      if (!ctx) return;
      const track = getTrack();
      const beat = 60 / track.bpm;
      while (state.nextNoteAt < ctx.currentTime + 0.18) {
        const note = track.pattern[state.noteIndex % track.pattern.length];
        playTone(note.f, state.nextNoteAt, note.d * beat);
        state.nextNoteAt += note.d * beat;
        state.noteIndex += 1;
      }
      state.lookAheadId = window.setTimeout(scheduleNotes, 90);
    }

    function startPlayback() {
      ensureAudioContext();
      state.isPlaying = true;
      if (!state.timerId) {
        state.timerId = window.setInterval(() => {
          state.currentTime += 1;
          if (state.currentTime >= getTrack().length) {
            if (state.loop) {
              state.currentTime = 0;
              state.noteIndex = 0;
            } else {
              pausePlayback();
              state.currentTime = getTrack().length;
            }
          }
          render();
        }, 1000);
      }
      if (state.audioContext) {
        state.nextNoteAt = state.audioContext.currentTime + 0.02;
        state.noteIndex = 0;
        stopScheduler();
        scheduleNotes();
      }
      render();
    }

    function pausePlayback() {
      state.isPlaying = false;
      if (state.timerId) {
        window.clearInterval(state.timerId);
        state.timerId = null;
      }
      stopScheduler();
      render();
    }

    function togglePlayback() {
      if (state.isPlaying) pausePlayback();
      else startPlayback();
    }

    function setTrack(nextIndex) {
      state.trackIndex = (nextIndex + tracks.length) % tracks.length;
      state.currentTime = 0;
      if (state.isPlaying) {
        startPlayback();
      } else {
        render();
      }
    }

    function setVariant(nextVariant) {
      state.variant = nextVariant;
      updateUrlVariant();
      render();
    }

    function shiftVariant(direction) {
      const currentIndex = variantKeys.indexOf(state.variant);
      const nextIndex = (currentIndex + direction + variantKeys.length) % variantKeys.length;
      setVariant(variantKeys[nextIndex]);
    }

    function progressPercent() {
      return clamp((state.currentTime / getTrack().length) * 100, 0, 100);
    }

    function sharedStateMarkup() {
      return `
        <section class="proto-state">
          <div><strong>Track</strong><span>${getTrack().title}</span></div>
          <div><strong>Status</strong><span>${state.isPlaying ? 'Playing' : 'Paused'}</span></div>
          <div><strong>Time</strong><span>${formatTime(state.currentTime)} / ${formatTime(getTrack().length)}</span></div>
          <div><strong>Volume</strong><span>${state.volume}%</span></div>
          <div><strong>Variant</strong><span>${state.variant}</span></div>
        </section>
      `;
    }

    function variantAMarkup(track) {
      return `
        <div class="music-grid variant-a">
          <section class="panel">
            <div class="panel-inner">
              <div class="hero-player" style="--cover-a:${track.colorA}; --cover-b:${track.colorB};">
                <div class="cover-stack">
                  <div class="cover">
                    <div>
                      <div class="cover-small">${track.artist}</div>
                      <div class="cover-badge"><span class="pulse-dot"></span>${state.isPlaying ? 'Live loop' : 'Ready'}</div>
                    </div>
                  </div>
                </div>
                <div class="track-meta">
                  <div class="track-caption">Variant A · cinematic cover player</div>
                  <h2 class="track-title">${track.title}</h2>
                  <p class="track-desc">${track.desc}</p>
                  <div class="pill-row">
                    <span class="pill">${track.mood}</span>
                    <span class="pill">${track.note}</span>
                    <span class="pill">${track.bpm} BPM</span>
                  </div>
                  <div class="control-row">
                    <button class="icon-btn" data-action="prev-track" aria-label="Previous track">⏮</button>
                    <button class="primary-btn" data-action="toggle-play">${state.isPlaying ? 'Pause loop' : 'Play loop'}</button>
                    <button class="icon-btn" data-action="next-track" aria-label="Next track">⏭</button>
                    <button class="ghost-btn" data-action="toggle-loop">${state.loop ? 'Loop on' : 'Loop off'}</button>
                  </div>
                  <div class="timeline">
                    <div class="timeline-labels"><span>${formatTime(state.currentTime)}</span><span>${formatTime(track.length)}</span></div>
                    <input type="range" min="0" max="${track.length}" value="${state.currentTime}" data-action="seek">
                  </div>
                </div>
              </div>
              <div class="stat-row">
                <div class="stat-card"><strong>${track.bpm}</strong><span>Tempo</span></div>
                <div class="stat-card"><strong>${Math.round(progressPercent())}%</strong><span>Track progress</span></div>
                <div class="stat-card"><strong>${state.loop ? 'Loop' : 'Single'}</strong><span>Playback mode</span></div>
              </div>
            </div>
          </section>
          <section class="panel">
            <div class="panel-inner">
              <div class="track-caption">Queue</div>
              <div class="playlist">
                ${tracks.map((item, index) => `
                  <button class="playlist-item ${index === state.trackIndex ? 'is-active' : ''}" data-action="select-track" data-index="${index}" style="--cover-a:${item.colorA}; --cover-b:${item.colorB};">
                    <div class="playlist-thumb"></div>
                    <div>
                      <strong>${item.title}</strong>
                      <span>${item.artist} · ${item.mood}</span>
                    </div>
                    <div class="playlist-length">${formatTime(item.length)}</div>
                  </button>
                `).join('')}
              </div>
              <ul class="proto-notes">
                <li>This layout answers whether a hero-first player feels engaging enough for a blog-side prototype.</li>
                <li>The player uses Web Audio API tones instead of external MP3 assets, so the page stays self-contained.</li>
              </ul>
            </div>
          </section>
        </div>
      `;
    }

    function variantBMarkup(track) {
      return `
        <section class="panel">
          <div class="variant-b-shell">
            <aside class="variant-b-sidebar">
              <div class="compact-head">
                <div class="compact-logo">SP</div>
                <div class="mini-note">Studio rack</div>
              </div>
              <div class="side-list">
                ${tracks.map((item, index) => `
                  <button class="side-item ${index === state.trackIndex ? 'is-active' : ''}" data-action="select-track" data-index="${index}">
                    <strong>${item.title}</strong>
                    <span>${item.artist}</span>
                  </button>
                `).join('')}
              </div>
            </aside>
            <div class="variant-b-main">
              <div class="vinyl-stage">
                <div>
                  <div class="track-caption">Variant B · studio rack</div>
                  <h2 class="track-title">${track.title}</h2>
                  <p class="track-desc">${track.desc}</p>
                </div>
                <div class="vinyl-disc ${state.isPlaying ? 'is-playing' : ''}"></div>
              </div>
              <div class="wave-panel">
                <div class="wave-bars ${state.isPlaying ? 'is-playing' : ''}">
                  ${track.bars.map((height) => `<span style="height:${state.isPlaying ? height : 18}px"></span>`).join('')}
                </div>
                <div class="control-row">
                  <button class="primary-btn" data-action="toggle-play">${state.isPlaying ? 'Pause' : 'Start session'}</button>
                  <button class="ghost-btn" data-action="prev-track">Previous</button>
                  <button class="ghost-btn" data-action="next-track">Next</button>
                </div>
                <div class="timeline">
                  <div class="timeline-labels"><span>${formatTime(state.currentTime)}</span><span>${formatTime(track.length)}</span></div>
                  <input type="range" min="0" max="${track.length}" value="${state.currentTime}" data-action="seek">
                </div>
                <div class="dial-row">
                  <div class="dial-card"><strong>${track.bpm}</strong><span class="mini-note">BPM</span></div>
                  <div class="dial-card"><strong>${track.mood}</strong><span class="mini-note">Mood</span></div>
                  <div class="dial-card">
                    <strong>${state.volume}%</strong>
                    <div class="volume-control"><input type="range" min="0" max="100" value="${state.volume}" data-action="volume"></div>
                  </div>
                </div>
              </div>
              ${sharedStateMarkup()}
            </div>
          </div>
        </section>
      `;
    }

    function variantCMarkup(track) {
      return `
        <div class="music-grid variant-c">
          <section class="panel">
            <div class="panel-inner">
              <div class="variant-c-head">
                <div>
                  <div class="track-caption">Variant C · timeline queue</div>
                  <h2 class="track-title">Queue as the primary view</h2>
                  <p class="track-desc">This variant answers a different question: can the player feel more editorial, where playlist flow matters more than a single album cover?</p>
                </div>
                <div class="pill-row">
                  <span class="pill">${state.isPlaying ? 'Playback active' : 'Playback idle'}</span>
                  <span class="pill">${state.loop ? 'Loop enabled' : 'Loop disabled'}</span>
                </div>
              </div>
              <div class="timeline-board">
                ${tracks.map((item, index) => `
                  <button class="timeline-card panel ${index === state.trackIndex ? 'is-active' : ''}" data-action="select-track" data-index="${index}">
                    <div class="timeline-index">0${index + 1}</div>
                    <div class="timeline-content">
                      <div class="timeline-content-top">
                        <div>
                          <strong>${item.title}</strong>
                          <span>${item.artist} · ${item.desc}</span>
                        </div>
                        <div class="timeline-badges">
                          <span class="timeline-badge">${item.mood}</span>
                          <span class="timeline-badge">${item.bpm} BPM</span>
                          <span class="timeline-badge">${formatTime(item.length)}</span>
                        </div>
                      </div>
                      ${index === state.trackIndex ? `
                        <div class="control-row">
                          <button class="primary-btn" data-action="toggle-play">${state.isPlaying ? 'Pause current' : 'Play current'}</button>
                          <button class="ghost-btn" data-action="prev-track">Previous</button>
                          <button class="ghost-btn" data-action="next-track">Next</button>
                        </div>
                        <div class="timeline">
                          <div class="timeline-labels"><span>${formatTime(state.currentTime)}</span><span>${formatTime(track.length)}</span></div>
                          <input type="range" min="0" max="${track.length}" value="${state.currentTime}" data-action="seek">
                        </div>
                      ` : ''}
                    </div>
                  </button>
                `).join('')}
              </div>
              ${sharedStateMarkup()}
            </div>
          </section>
        </div>
      `;
    }

    function switcherMarkup() {
      const current = variants.find((item) => item.key === state.variant) || variants[0];
      return `
        <div class="prototype-switcher" aria-label="Prototype variant switcher">
          <button class="switcher-btn" data-action="variant-prev" aria-label="Previous variant">←</button>
          <div class="switcher-label">${current.key} · ${current.name}<span>Prototype variant switcher</span></div>
          <button class="switcher-btn" data-action="variant-next" aria-label="Next variant">→</button>
        </div>
      `;
    }

    function render() {
      const track = getTrack();
      mount.innerHTML = `
        <div class="music-prototype">
          <div class="music-prototype-shell">
            <div class="music-prototype-kicker">Prototype skill in action</div>
            <h1 class="music-prototype-title">Lightweight Music Player</h1>
            <p class="music-prototype-subtitle">A self-contained player prototype for this Hexo blog. It synthesizes simple loops in the browser, surfaces player state on screen, and provides three clearly different layouts on one route.</p>
            ${state.variant === 'A' ? variantAMarkup(track) : state.variant === 'B' ? variantBMarkup(track) : variantCMarkup(track)}
          </div>
          ${switcherMarkup()}
        </div>
      `;
    }

    mount.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const action = target.getAttribute('data-action');
      if (action === 'toggle-play') togglePlayback();
      if (action === 'prev-track') setTrack(state.trackIndex - 1);
      if (action === 'next-track') setTrack(state.trackIndex + 1);
      if (action === 'toggle-loop') { state.loop = !state.loop; render(); }
      if (action === 'select-track') setTrack(Number(target.getAttribute('data-index')));
      if (action === 'variant-prev') shiftVariant(-1);
      if (action === 'variant-next') shiftVariant(1);
    });

    mount.addEventListener('input', (event) => {
      const target = event.target;
      const action = target.getAttribute('data-action');
      if (action === 'seek') {
        state.currentTime = Number(target.value);
        render();
      }
      if (action === 'volume') {
        state.volume = Number(target.value);
        render();
      }
    });

    window.addEventListener('keydown', (event) => {
      const tag = document.activeElement && document.activeElement.tagName;
      const isTyping = tag === 'INPUT' || tag === 'TEXTAREA' || (document.activeElement && document.activeElement.isContentEditable);
      if (isTyping) return;
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        shiftVariant(-1);
      }
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        shiftVariant(1);
      }
      if (event.code === 'Space') {
        event.preventDefault();
        togglePlayback();
      }
    });

    updateUrlVariant();
    render();
  })();
</script>
