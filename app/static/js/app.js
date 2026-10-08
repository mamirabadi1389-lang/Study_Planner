(() => {
  'use strict';

  /* ---------- helpers ---------- */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => [...document.querySelectorAll(sel)];
  const DIGITS = '۰۱۲۳۴۵۶۷۸۹';
  const faDigits = (s) => String(s).replace(/\d/g, (d) => DIGITS[d]);
  const fa = (n, max = 2) =>
    Number(n).toLocaleString('fa-IR', { maximumFractionDigits: max });
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));

  const DAYS = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'];
  const DAYS_SHORT = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
  const PRIORITY = { 1: 'بالا', 2: 'متوسط', 3: 'کم' };
  const THEMES = [
    ['neon', 'نئون', '#7c5cff', '#19e3c1'],
    ['ocean', 'اقیانوس', '#2f8cff', '#22d3ee'],
    ['sunset', 'غروب', '#ff7a45', '#ff3d81'],
    ['forest', 'جنگل', '#2fbf71', '#b6e03a'],
    ['light', 'روشن', '#6b4cff', '#12b8a0'],
  ];

  function todayIso() {
    return new Date().toLocaleDateString('en-CA');
  }
  const state = { day: todayIso(), theme: 'neon' };

  const at = (iso) => new Date(`${iso}T00:00:00`);
  const fmtDate = (iso) => at(iso).toLocaleDateString('fa-IR', { dateStyle: 'medium' });
  const shortDate = (iso) =>
    at(iso).toLocaleDateString('fa-IR', { month: 'numeric', day: 'numeric' });
  const weekdayShort = (iso) => DAYS_SHORT[(at(iso).getDay() + 1) % 7];
  const daysLeft = (iso) => Math.round((at(iso) - at(todayIso())) / 864e5);
  const minutesText = (m) => {
    const h = Math.floor(m / 60);
    const r = m % 60;
    return h ? `${fa(h)} ساعت و ${fa(r)} دقیقه` : `${fa(r)} دقیقه`;
  };

  const setHtml = (sel, html) => { $(sel).innerHTML = html; };
  const setVal = (sel, value) => {
    const el = $(sel);
    if (document.activeElement !== el) el.value = value;
  };
  const emptyBox = (text) => `<p class="muted center">${text}</p>`;

  const toast = (msg, bad = false) => {
    const node = document.createElement('div');
    node.className = `toast${bad ? ' bad' : ''}`;
    node.textContent = msg;
    $('#toast-host').appendChild(node);
    setTimeout(() => node.remove(), 3500);
  };

  /* ---------- theme ---------- */
  const applyTheme = (name) => {
    state.theme = name;
    document.documentElement.dataset.theme = name;
    $$('.theme-opt').forEach((b) =>
      b.classList.toggle('active', b.dataset.theme === name));
  };
  const changeTheme = async (name) => {
    applyTheme(name);
    await Api.put('/settings', { theme: name });
  };

  /* ---------- row builders ---------- */
  const empty = (text) => `<li class="empty">${text}</li>`;
  const dot = (c) => `<i class="dot" style="--c:${esc(c)}"></i>`;
  const delBtn = (kind, id) =>
    `<button class="x" data-act="del" data-kind="${kind}" data-id="${id}" title="حذف">✕</button>`;
  const range = (s) => `${faDigits(s.start)} – ${faDigits(s.end)}`;

  const taskRow = (t) => `
    <li>
      <button class="check ${t.done ? 'done' : ''}" data-act="toggle"
              data-id="${t.id}" data-done="${t.done}"></button>
      <span class="grow ${t.done ? 'strike' : ''}">${esc(t.title)}</span>
      <span class="tag p${t.priority}">${PRIORITY[t.priority]}</span>
      ${delBtn('tasks', t.id)}
    </li>`;

  const classRow = (s) =>
    `<li>${dot(s.color)}${esc(s.name)}<em>${range(s)}</em></li>`;

  const reminderRow = (r) => {
    const when = new Date(r.due_at).toLocaleString('fa-IR', {
      dateStyle: 'short', timeStyle: 'short',
    });
    return `<li><span class="grow ${r.fired ? 'strike' : ''}">⏰ ${esc(r.title)}</span>
      <em>${esc(when)}</em>${delBtn('reminders', r.id)}</li>`;
  };

  const examRow = (e) => {
    const left = daysLeft(e.day);
    let badge = '';
    if (e.grade === null) {
      badge = left < 0 ? 'گذشته' : left === 0 ? 'امروز' : `${fa(left)} روز مانده`;
    }
    return `<li class="exam">${dot(e.color)}
      <span class="grow"><b>${esc(e.title)}</b>
        <small class="muted"> ${esc(e.course)} · ${fmtDate(e.day)}</small></span>
      ${badge ? `<span class="tag">${badge}</span>` : ''}
      <input class="grade-input" type="number" step="0.25" min="0"
             max="${e.max_grade}" value="${e.grade ?? ''}"
             placeholder="نمره" data-id="${e.id}">
      <small class="muted">/ ${fa(e.max_grade)}</small>
      ${delBtn('exams', e.id)}</li>`;
  };

  /* ---------- focus timer ---------- */
  const timer = { total: 1500, left: 1500, running: false, endAt: 0, tick: null };

  const clock = (sec) => faDigits(
    `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`
  );
  const drawTimer = () => {
    $('#timer').textContent = clock(timer.left);
    $('#timer-bar').style.width = `${((timer.total - timer.left) / timer.total) * 100}%`;
    $('#timer-btn').textContent = timer.running ? 'مکث' : 'شروع';
  };
  const stopTimer = () => {
    clearInterval(timer.tick);
    timer.running = false;
  };
  const finishFocus = async () => {
    stopTimer();
    const minutes = Math.round(timer.total / 60);
    timer.left = timer.total;
    drawTimer();
    try {
      await Api.post('/focus', { minutes });
      toast(`🎯 ${fa(minutes)} دقیقه تمرکز ثبت شد`);
      if (window.Notification && Notification.permission === 'granted') {
        new Notification('تمرکز تموم شد', { body: `${minutes} دقیقه` });
      }
      await loadAll();
    } catch (err) {
      toast(err.message, true);
    }
  };
  const onTick = () => {
    timer.left = Math.max(0, Math.round((timer.endAt - Date.now()) / 1000));
    drawTimer();
    if (timer.left === 0) finishFocus();
  };
  const toggleTimer = () => {
    if (timer.running) {
      stopTimer();
    } else {
      timer.running = true;
      timer.endAt = Date.now() + timer.left * 1000;
      timer.tick = setInterval(onTick, 500);
    }
    drawTimer();
  };
  const resetTimer = () => {
    stopTimer();
    timer.left = timer.total;
    drawTimer();
  };

  /* ---------- render ---------- */
  const render = (data) => {
    const { courses, schedule, tasks, reminders, exams, summary, stats, settings } = data;
    const p = summary.progress;
    const goal = Number(settings.daily_goal) || 5;
    const doneToday = summary.tasks.filter((t) => t.done).length;
    const todayStats = stats.days[stats.days.length - 1];
    const g = summary.gpa;
    const gpaHtml = g === null ? '—' : `${fa(g)}<small>/ ۲۰</small>`;

    applyTheme(settings.theme);
    $('#greet').textContent = settings.name
      ? `سلام ${settings.name}، آماده‌ای؟` : 'سلام، آماده‌ای؟';
    const dateText = new Date().toLocaleDateString('fa-IR', {
      weekday: 'long', day: 'numeric', month: 'long',
    });
    $('#greet-sub').textContent =
      `${dateText} — امروز ${fa(summary.classes.length)} کلاس و ${fa(summary.tasks.length)} کار داری`;

    /* level, goal, streak */
    $('#ring').style.setProperty('--p', p.percent);
    $('#lvl').textContent = fa(p.level);
    $('#lvl-text').textContent = `${fa(p.percent)}٪ تا لول بعدی — ${fa(p.xp)} امتیاز`;
    $('#lvl-bar').style.width = `${p.percent}%`;
    $('#rank').textContent = `🏅 ${p.rank}`;

    $('#goal-ring').style.setProperty('--p', Math.min(100, Math.round((doneToday / goal) * 100)));
    $('#goal-num').textContent = fa(doneToday);
    $('#goal-of').textContent = `از ${fa(goal)}`;
    $('#goal-text').textContent = doneToday >= goal
      ? 'هدف امروز کامل شد 🎉' : `${fa(goal - doneToday)} کار تا هدف امروز`;

    $('#streak-now').innerHTML = `${fa(stats.streak.current)}<small>روز</small>`;
    $('#streak-best').textContent = `بهترین استریک: ${fa(stats.streak.best)} روز`;

    /* dashboard lists */
    setHtml('#dash-classes', summary.classes.map(classRow).join('') || empty('امروز کلاسی نداری'));
    setHtml('#dash-tasks', summary.tasks.map(taskRow).join('') || empty('کاری برای امروز ثبت نشده'));
    setHtml('#dash-reminders',
      reminders.filter((r) => !r.fired).slice(0, 4).map(reminderRow).join('')
      || empty('یادآوری نداری'));

    const ex = summary.next_exam;
    setHtml('#dash-exam', ex
      ? `<div class="countdown"><strong>${fa(ex.days_left)}</strong><span>روز مانده</span></div>
         <p class="muted">${esc(ex.course)} — ${esc(ex.title)}</p>`
      : '<p class="muted">امتحان پیش‌رویی ثبت نشده</p>');

    setHtml('#dash-gpa', gpaHtml);
    $('#dash-gpa-bar').style.width = `${g === null ? 0 : (g / 20) * 100}%`;
    setHtml('#grade-gpa', gpaHtml);
    $('#grade-xp').textContent = fa(p.xp);

    /* focus timer */
    $('#focus-today').textContent = `امروز ${minutesText(todayStats.focus)} تمرکز داشتی`;
    const target = (Number(settings.focus_minutes) || 25) * 60;
    if (!timer.running && timer.left === timer.total && timer.total !== target) {
      timer.total = target;
      timer.left = target;
    }
    drawTimer();

    /* week / courses */
    const options = courses.length
      ? courses.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join('')
      : '<option value="">ابتدا یک درس اضافه کن</option>';
    setHtml('#slot-course', options);
    setHtml('#exam-course', options);

    setHtml('#course-list', courses.map((c) =>
      `<li>${dot(c.color)}${esc(c.name)}<em>${fa(c.credits)} واحد</em>${delBtn('courses', c.id)}</li>`
    ).join('') || empty('درسی ثبت نشده'));

    setHtml('#week-grid', DAYS.map((name, i) => {
      const slots = schedule.filter((s) => s.weekday === i).map((s) => `
        <div class="slot" style="--c:${esc(s.color)}">
          <b>${esc(s.name)}</b><small>${range(s)}</small>${delBtn('schedule', s.id)}
        </div>`).join('');
      const today = i === summary.weekday ? 'today' : '';
      return `<div class="day glass ${today}"><h4>${name}</h4>${slots || '<p class="muted">—</p>'}</div>`;
    }).join(''));

    /* tasks / reminders / exams */
    setHtml('#task-list', tasks.map(taskRow).join('') || empty('کاری برای این روز نیست'));
    setHtml('#reminder-list', reminders.map(reminderRow).join('') || empty('یادآوری ثبت نشده'));
    setHtml('#exam-list', exams.map(examRow).join('') || empty('امتحانی ثبت نشده'));

    /* grades */
    setHtml('#grade-courses', summary.courses.map((c) => `
      <li class="course-avg">${dot(c.color)}<span>${esc(c.course)}</span>
        <div class="bar"><span style="width:${(c.average / 20) * 100}%"></span></div>
        <em>${fa(c.average)}</em></li>`).join('') || empty('هنوز نمره‌ای ثبت نشده'));

    setHtml('#chart-scores', stats.scores.length
      ? Charts.line(stats.scores.map((s) => ({
        label: shortDate(s.day), value: s.score, tip: `${s.course} — ${s.title}`,
      })))
      : emptyBox('بعد از ثبت اولین نمره، نمودار اینجا نشون داده می‌شه'));

    /* stats */
    const week = stats.days.slice(-7);
    const weekChart = Charts.bar(week.map((d) => ({
      label: weekdayShort(d.day), value: d.done,
      active: d.day === todayIso(), tip: fmtDate(d.day),
    })));
    setHtml('#chart-week-dash', weekChart);
    setHtml('#chart-week', weekChart);
    setHtml('#chart-focus', Charts.bar(week.map((d) => ({
      label: weekdayShort(d.day), value: d.focus,
      active: d.day === todayIso(), tip: fmtDate(d.day),
    }))));

    const t = stats.totals;
    $('#t-done').textContent = fa(t.tasks_done);
    $('#t-rate').textContent = `${fa(t.tasks_total ? (t.tasks_done / t.tasks_total) * 100 : 0, 0)}٪`;
    $('#t-focus').textContent = minutesText(t.focus_minutes);
    $('#t-exams').textContent = `${fa(t.graded)} از ${fa(t.exams)}`;

    const totalHours = stats.hours.reduce((s, h) => s + h.hours, 0);
    setHtml('#donut-hours', stats.hours.length
      ? Charts.donut(
        stats.hours.map((h) => ({ label: h.course, value: h.hours, color: h.color })),
        fa(totalHours, 1), 'ساعت در هفته')
      : emptyBox('درس‌ها رو به برنامه هفتگی اضافه کن'));
    setHtml('#hours-legend', stats.hours.map((h) =>
      `<li>${dot(h.color)}${esc(h.course)}<em>${fa(h.hours, 1)} ساعت</em></li>`).join(''));

    setHtml('#heatmap', Charts.heat(stats.days, fmtDate));
    setHtml('#badges', stats.achievements.map((a) => `
      <div class="badge ${a.unlocked ? 'on' : ''}">
        <span>${a.icon}</span><b>${esc(a.title)}</b><small>${esc(a.desc)}</small>
      </div>`).join(''));

    /* settings form */
    setVal('#set-name', settings.name);
    setVal('#set-goal', settings.daily_goal);
    setVal('#set-focus', settings.focus_minutes);
  };

  const loadAll = async () => {
    const [courses, schedule, tasks, reminders, exams, summary, stats, settings] =
      await Promise.all([
        Api.get('/courses'),
        Api.get('/schedule'),
        Api.get(`/tasks?day=${state.day}`),
        Api.get('/reminders'),
        Api.get('/exams'),
        Api.get('/summary'),
        Api.get('/stats'),
        Api.get('/settings'),
      ]);
    render({ courses, schedule, tasks, reminders, exams, summary, stats, settings });
  };
  const safeLoad = () => loadAll().catch((e) => toast(e.message, true));

  const showView = (name) => {
    $$('.view').forEach((v) => v.classList.toggle('active', v.id === `view-${name}`));
    $$('.nav-item').forEach((n) => n.classList.toggle('active', n.dataset.view === name));
  };

  /* ---------- forms ---------- */
  const forms = {
    'course-form': (d) => Api.post('/courses', d),
    'slot-form': (d) => Api.post('/schedule', d),
    'task-form': (d) => Api.post('/tasks', { ...d, day: state.day }),
    'reminder-form': (d) => Api.post('/reminders', d),
    'exam-form': (d) => Api.post('/exams', d),
    'settings-form': (d) => Api.put('/settings', d),
  };

  document.addEventListener('submit', async (e) => {
    const send = forms[e.target.id];
    if (!send) return;
    e.preventDefault();
    try {
      await send(Object.fromEntries(new FormData(e.target)));
      e.target.reset();
      await loadAll();
      toast('ذخیره شد ✓');
    } catch (err) {
      toast(err.message, true);
    }
  });

  /* ---------- clicks ---------- */
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-act]');
    if (!btn) return;
    const { act, id, kind, view, focus } = btn.dataset;

    if (act === 'view') {
      showView(view);
      if (focus) $(`#${focus}`).focus();
      return;
    }
    if (act === 'timer-toggle') return toggleTimer();
    if (act === 'timer-reset') return resetTimer();

    try {
      if (act === 'theme') {
        await changeTheme(btn.dataset.theme);
        return;
      }
      if (act === 'cycle-theme') {
        const i = THEMES.findIndex(([name]) => name === state.theme);
        await changeTheme(THEMES[(i + 1) % THEMES.length][0]);
        return;
      }
      if (act === 'toggle') {
        await Api.patch(`/tasks/${id}`, { done: btn.dataset.done !== '1' });
      } else if (act === 'del') {
        if (!confirm('حذف شود؟')) return;
        await Api.del(`/${kind}/${id}`);
      } else {
        return;
      }
      await loadAll();
    } catch (err) {
      toast(err.message, true);
    }
  });

  document.addEventListener('change', async (e) => {
    try {
      if (e.target.matches('.grade-input')) {
        const v = e.target.value;
        await Api.patch(`/exams/${e.target.dataset.id}`, {
          grade: v === '' ? null : Number(v),
        });
        await loadAll();
      } else if (e.target.id === 'task-day') {
        state.day = e.target.value || todayIso();
        await loadAll();
      }
    } catch (err) {
      toast(err.message, true);
    }
  });

  /* ---------- reminders ---------- */
  const pollReminders = async () => {
    try {
      const due = await Api.post('/reminders/poll');
      due.forEach((r) => {
        toast(`⏰ ${r.title}`);
        if (window.Notification && Notification.permission === 'granted') {
          new Notification('یادآور', { body: r.title });
        }
      });
      if (due.length) await loadAll();
    } catch (_) { /* ignore */ }
  };

  document.addEventListener('click', () => {
    if (window.Notification && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, { once: true });

  /* ---------- init ---------- */
  setHtml('#themes', THEMES.map(([name, label, c1, c2]) => `
    <button class="theme-opt" data-act="theme" data-theme="${name}">
      <span class="sw" style="background:linear-gradient(135deg, ${c1}, ${c2})"></span>${label}
    </button>`).join(''));
  $('#task-day').value = state.day;
  showView('dashboard');
  safeLoad().finally(() => document.dispatchEvent(new Event('app:ready')));
  pollReminders();
  setInterval(pollReminders, 30000);
})();