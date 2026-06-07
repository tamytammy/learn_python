'use strict';

// ── Helpers ──────────────────────────────────────────────────────────────────

function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function statusBadge(status) {
  const map = {
    completed:   ['badge-completed',   '已完成'],
    in_progress: ['badge-in_progress', '進行中'],
    not_started: ['badge-not_started', '未開始'],
  };
  const [cls, label] = map[status] ?? map.not_started;
  return `<span class="status-badge ${cls}">${label}</span>`;
}

function checkIcon(done) {
  return done
    ? `<svg class="ex-icon done" viewBox="0 0 16 16" fill="none" aria-hidden="true">
         <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5"/>
         <path d="M5 8l2 2 4-4" stroke="currentColor" stroke-width="1.5"
               stroke-linecap="round" stroke-linejoin="round"/>
       </svg>`
    : `<svg class="ex-icon pending" viewBox="0 0 16 16" fill="none" aria-hidden="true">
         <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5"
                 stroke-dasharray="3.5 2.5"/>
       </svg>`;
}


// ── Renderers ────────────────────────────────────────────────────────────────

function renderWeeks(weeks) {
  const grid = document.getElementById('weeks-grid');
  if (!weeks?.length) { grid.innerHTML = '<div class="loading">無學習資料</div>'; return; }

  grid.innerHTML = weeks.map(w => {
    const done  = w.exercises.filter(e => e.status === 'completed').length;
    const total = w.exercises.length;
    const pct   = total > 0 ? Math.round((done / total) * 100) : 0;

    const exItems = w.exercises.map(e => {
      const isDone = e.status === 'completed';
      return `<li class="exercise-item ${isDone ? 'done' : ''}">
        ${checkIcon(isDone)}
        <span>${esc(e.id)} · ${esc(e.title)}</span>
      </li>`;
    }).join('');

    return `
      <article class="week-card status-${w.status}">
        <div class="week-header">
          <div>
            <div class="week-label">WEEK ${w.id}</div>
            <div class="week-title">${esc(w.title)}</div>
            <div class="week-subtitle">${esc(w.subtitle)}</div>
          </div>
          ${statusBadge(w.status)}
        </div>

        <div class="progress-wrap">
          <div class="progress-track">
            <div class="progress-fill fill-${w.status}" style="width:${pct}%"></div>
          </div>
          <div class="progress-label">${done} / ${total} 練習完成</div>
        </div>

        <ul class="exercise-list">${exItems}</ul>
      </article>`;
  }).join('');
}

function renderSkills(skills) {
  const wrapper = document.getElementById('skills-wrapper');
  const sections = [
    { key: 'python',  label: 'Python',   cls: 'tag-python'  },
    { key: 'eda',     label: 'EDA 知識', cls: 'tag-eda'     },
    { key: 'tools',   label: '工具',     cls: 'tag-tools'   },
    { key: 'pending', label: '待解鎖',   cls: 'tag-pending' },
  ];

  wrapper.innerHTML = sections.map(s => {
    const tags = (skills[s.key] ?? []);
    if (!tags.length) return '';
    return `
      <div class="skill-group">
        <span class="skill-group-label">${s.label}</span>
        <div class="skill-tags">
          ${tags.map(t => `<span class="skill-tag ${s.cls}">${esc(t)}</span>`).join('')}
        </div>
      </div>`;
  }).join('');
}

function renderTimeline(commits) {
  const tl = document.getElementById('timeline');
  if (!commits?.length) {
    tl.innerHTML = `<div class="timeline-empty">
      $ git log --oneline<br>
      <span style="opacity:.5">// 尚無提交記錄 — 完成練習後執行 @save</span>
    </div>`;
    return;
  }

  tl.innerHTML = commits.map(c => `
    <div class="tl-item">
      <div class="tl-gutter">
        <div class="tl-dot"></div>
        <div class="tl-line"></div>
      </div>
      <div class="tl-body">
        <div class="tl-msg">${esc(c.message)}</div>
        <div class="tl-meta">
          <span class="tl-hash">${esc(c.hash)}</span>
          <span class="tl-date">${esc(c.date)}</span>
        </div>
      </div>
    </div>`).join('');
}

function renderStats(data) {
  const completedWeeks = (data.weeks ?? []).filter(w => w.status === 'completed').length;
  const completedEx    = (data.weeks ?? []).reduce(
    (n, w) => n + w.exercises.filter(e => e.status === 'completed').length, 0
  );
  const commits = (data.commits ?? []).length;

  let days = 0;
  if (data.meta?.start_date) {
    const start = new Date(data.meta.start_date);
    days = Math.max(1, Math.floor((Date.now() - start) / 86_400_000) + 1);
  }

  document.getElementById('stat-weeks').textContent     = completedWeeks;
  document.getElementById('stat-exercises').textContent = completedEx;
  document.getElementById('stat-commits').textContent   = commits;
  document.getElementById('stat-days').textContent      = days;
}


// ── Entry point ──────────────────────────────────────────────────────────────

async function main() {
  let data;
  try {
    const res = await fetch('data/progress.json?t=' + Date.now());
    if (!res.ok) throw new Error(res.statusText);
    data = await res.json();
  } catch (err) {
    console.error('無法載入 progress.json:', err);
    document.getElementById('weeks-grid').innerHTML =
      '<div class="loading">⚠ 無法載入資料 — 請確認已執行 generate_report.py</div>';
    return;
  }

  document.getElementById('last-updated').textContent =
    `更新於 ${data.meta?.last_updated ?? '--'}`;

  renderStats(data);
  renderWeeks(data.weeks ?? []);
  renderSkills(data.skills ?? {});
  renderTimeline(data.commits ?? []);
}

main();
