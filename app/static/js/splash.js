(() => {
  'use strict';

  const splash = document.getElementById('splash');
  if (!splash) return;

  /* ---------- tweak here ---------- */
  const TITLE = 'STUDY PLANNER';
  const TIMING = {
    start: 250,       // black screen before the mark
    mark: 1400,       // mark intro animation
    gap: 150,
    box: 400,         // rectangle opening
    perChar: 60,      // typing speed
    afterType: 200,
    fill: 1400,       // loading line
    afterFill: 350,
    out: 650,         // fade out (matches CSS)
    failsafe: 15000,
  };
  const STATUS = [
    [0, 'INITIALIZING'],
    [25, 'LOADING MODULES'],
    [55, 'SYNCING DATABASE'],
    [85, 'BUILDING INTERFACE'],
    [100, 'READY'],
  ];
  /* -------------------------------- */

  const $ = (sel) => splash.querySelector(sel);
  let ready = false;
  let skipped = false;

  document.addEventListener('app:ready', () => { ready = true; });
  splash.addEventListener('click', () => { skipped = true; });
  document.addEventListener('keydown', () => { skipped = true; }, { once: true });

  const wait = (ms) =>
    new Promise((resolve) => setTimeout(resolve, skipped ? 0 : ms));

  const typeTitle = async () => {
    const el = $('#sp-text');
    for (const ch of TITLE) {
      if (skipped) { el.textContent = TITLE; return; }
      el.textContent += ch;
      await wait(ch === ' ' ? TIMING.perChar * 2 : TIMING.perChar);
    }
  };

  const fillBar = () => new Promise((resolve) => {
    const bar = $('#sp-fill');
    const pct = $('#sp-pct');
    const status = $('#sp-status');
    const t0 = performance.now();

    const step = (now) => {
      const f = Math.min((now - t0) / TIMING.fill, 1);
      const eased = f < 0.5 ? 2 * f * f : 1 - ((-2 * f + 2) ** 2) / 2;
      if (now - t0 > TIMING.failsafe) ready = true;
      const value = skipped ? 1 : Math.min(eased, ready ? 1 : 0.96);
      const percent = Math.round(value * 100);

      bar.style.width = `${value * 100}%`;
      pct.textContent = `${percent}%`;
      status.textContent = STATUS.filter(([t]) => percent >= t).pop()[1];

      if (value >= 1) resolve();
      else requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });

  const finish = async () => {
    document.body.classList.remove('booting');
    splash.classList.add('out');
    await new Promise((resolve) => setTimeout(resolve, TIMING.out + 100));
    splash.remove();
  };

  const run = async () => {
    await wait(TIMING.start);
    $('.sp-mark').classList.add('on');
    await wait(TIMING.mark);
    $('.sp-mark').classList.add('idle');
    await wait(TIMING.gap);
    $('.sp-box').classList.add('on');
    await wait(TIMING.box);
    await typeTitle();
    $('.sp-caret').classList.add('off');
    await wait(TIMING.afterType);
    $('.sp-load').classList.add('on');
    await fillBar();
    $('.sp-track').classList.add('done');
    await wait(TIMING.afterFill);
    await finish();
  };

  run();
})();