// Mobile Dashboard Update Script - Sync with Desktop Best Features
// This script contains the enhanced JavaScript sections to patch into mobile.html

// ========== 1. ENHANCED MIND STATE WITH DECISIONS LOG ==========
const enhancedRefreshMind = `
async function refreshMind() {
    const data = await fetchJSON('/mind-state.json');
    if (!data) return;

    const card = document.getElementById('mind-card');
    const dot = document.getElementById('mind-dot');
    const content = document.getElementById('mind-content');
    const sections = document.getElementById('mind-sections');
    const hasActiveSubs = (data.subAgents || []).some(s => s.status === 'active');
    const isActive = data.task != null || hasActiveSubs;

    card.classList.toggle('active', isActive);
    card.classList.toggle('glow', isActive);
    dot.classList.toggle('active', isActive);
    window._mmModel = data.model || 'opus';
    refreshMindMap(isActive, data.steps);

    // Sub-agent lobster satellites
    const subs = data.subAgents || [];
    const saKey = JSON.stringify(subs);
    if (saKey !== window._lastSubAgentKey) {
        window._lastSubAgentKey = saKey;
        updateSubagentLobsters(subs);
    }

    if (!isActive) {
        content.style.display = '';
        const lastGoal = data.lastTask && data.lastTask !== 'Working...' ? \`<div style="color:rgba(255,255,255,0.35);font-size:0.65rem;margin-top:0.3rem;">Last: \${esc(data.lastTask)}</div>\` : '';
        content.innerHTML = '<div class="mind-idle">Idle — waiting for Josh<span class="mind-idle-dots"></span></div>' + lastGoal;
        sections.style.display = 'none';
        return;
    }

    // Hide idle, show sections
    content.style.display = 'none';
    sections.style.display = '';

    // Model/tool color map
    const modelColors = {opus:'#4ade80', claude:'#4ade80', sonnet:'#8b5cf6', whisper:'#facc15', ollama:'#f97316', browser:'#3b82f6', x:'#1d9bf0', twitter:'#1d9bf0', sorare:'#ffd700', dexscreener:'#a855f7', gmail:'#ef4444', whatsapp:'#25d366', finnhub:'#06b6d4', coingecko:'#06b6d4', sd:'#ec4899'};
    const activeColor = modelColors[(data.model||'').toLowerCase()] || 'var(--accent)';

    // Goal / Objective
    const goalEl = document.getElementById('mind-task-text');
    goalEl.textContent = data.task || 'Awaiting instructions...';
    goalEl.style.color = activeColor;

    // Thinking & Decisions
    const thoughtEl = document.getElementById('mind-thought-text');
    thoughtEl.textContent = data.thought || 'Ready for your next request.';
    thoughtEl.style.color = activeColor;

    // Actions & Tools (steps) + Decisions Log
    const stepsEl = document.getElementById('mind-steps');
    if (data.steps && data.steps.length) {
        const indicators = { done: '✓', active: '●', pending: '○' };
        // Deduplicate consecutive steps
        const dedupedSteps = data.steps.reduce((acc, step) => {
            if (!acc.length || (step.label||step.text||'') !== (acc[acc.length-1].label||acc[acc.length-1].text||'')) acc.push(step);
            else acc[acc.length-1] = step;
            return acc;
        }, []);
        stepsEl.innerHTML = dedupedSteps.map(step => {
            const s = step.status || 'pending';
            const stepColor = modelColors[(step.tool||'').toLowerCase()] || 'var(--accent)';
            return \`<div class="mind-step \${s}" style="color:\${stepColor}"><span class="mind-step-icon">\${indicators[s]||'○'}</span><span>\${esc(step.label||step.text)}</span></div>\`;
        }).join('');
    } else {
        stepsEl.innerHTML = '';
    }
    
    // Append decisions log (NEW FEATURE from desktop)
    if (data.decisions && data.decisions.length > 0) {
        const decisionsHtml = data.decisions.slice(-6).reverse().map(d => {
            const time = d.time || '';
            const icon = d.icon || '●';
            const mColor = d.model ? (modelColors[d.model.toLowerCase()] || 'rgba(255,255,255,0.5)') : 'rgba(255,255,255,0.5)';
            return \`<div style="display:flex;gap:0.3rem;align-items:flex-start;padding:0.15rem 0;border-left:2px solid \${mColor};padding-left:0.4rem;margin:0.1rem 0;color:rgba(255,255,255,0.6);font-size:0.6rem;line-height:1.3;">
                <span style="flex-shrink:0;font-size:0.5rem;color:rgba(255,255,255,0.25);min-width:36px;">\${time}</span>
                <span>\${icon} \${d.text||''}</span>
            </div>\`;
        }).join('');
        if (decisionsHtml) {
            stepsEl.innerHTML += '<div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:0.3rem;padding-top:0.3rem;">' + decisionsHtml + '</div>';
        }
    }
}
`;

// ========== 2. TICKER MARKET STATUS DOTS ==========
const enhancedRefreshTicker = `
async function refreshTicker() {
    const data = await fetchJSON('/api/ticker').then(r => r, () => fetchJSON('/ticker.json')).catch(() => null);
    if (!data) return;
    tickerData = data;
    if (tickerExpanded) renderTickerPrices(data);
    const fmt = (v, isDollar) => {
        if (v == null) return '--';
        if (isDollar) return v >= 1000 ? '$' + v.toLocaleString('en',{maximumFractionDigits:0}) : '$' + v.toFixed(2);
        return v.toFixed(2) + '%';
    };
    const items = {
        btc: data.btc, eth: data.eth, sol: data.sol,
        ndaq: data.nasdaq || data.ndaq
    };
    // Market status dots — crypto 24/7, stocks M-F 9:30-4 ET (NEW FEATURE)
    const now = new Date();
    const et = new Date(now.toLocaleString('en-US', {timeZone:'America/New_York'}));
    const day = et.getDay(), h = et.getHours(), m = et.getMinutes();
    const stockOpen = day >= 1 && day <= 5 && (h > 9 || (h === 9 && m >= 30)) && h < 16;
    const marketOpen = { btc: true, eth: true, sol: true, ndaq: stockOpen };
    for (const [key, val] of Object.entries(items)) {
        const el = document.getElementById('tk-' + key);
        if (!el || !val) continue;
        const chEl = el.querySelector('.tk-c');
        const ch = val.change24h;
        chEl.textContent = ch != null ? (ch >= 0 ? '+' : '') + ch.toFixed(1) + '%' : '--%';
        chEl.className = 'tk-c ' + (ch > 0 ? 'pos' : ch < 0 ? 'neg' : '');
        // Market status dot (NEW)
        let dot = el.querySelector('.tk-dot');
        if (!dot) { dot = document.createElement('span'); dot.className = 'tk-dot'; el.prepend(dot); }
        const open = marketOpen[key];
        dot.style.cssText = 'display:inline-block;width:4px;height:4px;border-radius:50%;margin-right:1px;background:' + (open ? '#4ade80' : '#ef4444');
    }
}
`;

// ========== 3. X THREAD HISTORY WITH NEON EMOJIS ==========
const neonEmojiFunction = `
function dtNeonEmoji(text) {
    const neonStyle = 'display:inline-block;color:#4ade80;text-shadow:0 0 6px #4ade80,0 0 12px #4ade8088;font-size:0.85em;vertical-align:middle;';
    const map = {
        '🌪️': \`<svg style="\${neonStyle}width:1em;height:1em;" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2"><path d="M4 8h14c1 0 2-1 2-2s-1-2-2-2H6"/><path d="M3 12h18c1 0 2 1 2 2s-1 2-2 2H8"/><path d="M6 16h8c1 0 2 1 2 2s-1 2-2 2H10"/></svg>\`,
        '🤖': \`<svg style="\${neonStyle}width:1em;height:1em;" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2"><rect x="4" y="6" width="16" height="14" rx="3"/><circle cx="9" cy="13" r="1.5" fill="#4ade80"/><circle cx="15" cy="13" r="1.5" fill="#4ade80"/><line x1="12" y1="2" x2="12" y2="6"/><circle cx="12" cy="2" r="1" fill="#4ade80"/></svg>\`,
        '💼': \`<svg style="\${neonStyle}width:1em;height:1em;" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2"><rect x="2" y="7" width="20" height="13" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>\`,
        '📈': \`<svg style="\${neonStyle}width:1em;height:1em;" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>\`,
        '🔥': \`<svg style="\${neonStyle}width:1em;height:1em;" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" style="filter:drop-shadow(0 0 4px #f59e0b)"><path d="M12 22c4-3 7-6 7-10a7 7 0 00-14 0c0 4 3 7 7 10z"/></svg>\`,
        '📰': \`<svg style="\${neonStyle}width:1em;height:1em;" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="7" y1="8" x2="17" y2="8"/><line x1="7" y1="12" x2="13" y2="12"/></svg>\`
    };
    let result = text;
    for (const [emoji, svg] of Object.entries(map)) {
        result = result.split(emoji).join(svg);
    }
    return result;
}
`;

// ========== 4. SORARE DAILY TASKS & CRAFTING ==========
const enhancedRefreshSorare = `
async function refreshSorare() {
    const [data, tasksData, craftData] = await Promise.all([
        fetchJSON('/sorare-mobile.json'),
        fetchJSON('/sorare-daily-tasks.json'),
        fetchJSON('/sorare-crafting-status.json')
    ]);

    // Daily tasks (NEW FEATURE)
    const tasksEl = document.getElementById('sorare-daily-tasks');
    if (tasksData && tasksData.tasks && tasksData.tasks.length > 0) {
        let tHtml = '<div class="sorare-section-label">📋 Daily Tasks</div>';
        tHtml += '<div class="sorare-lineup" style="padding:0.3rem 0.5rem;">';
        tasksData.tasks.forEach(t => {
            const doneClass = t.done ? ' done' : '';
            const checkIcon = t.done ? '✓' : '';
            const timeStr = t.doneAt ? new Date(t.doneAt).toLocaleTimeString([], {hour:'numeric',minute:'2-digit'}) : '';
            tHtml += '<div class="sorare-task">';
            tHtml += '<div class="sorare-task-check' + doneClass + '">' + checkIcon + '</div>';
            tHtml += '<span class="sorare-task-name' + doneClass + '">' + t.name + '</span>';
            if (timeStr) tHtml += '<span class="sorare-task-time">' + timeStr + '</span>';
            tHtml += '</div>';
        });
        tHtml += '</div>';
        tasksEl.innerHTML = tHtml;
    } else {
        tasksEl.innerHTML = '';
    }

    // Crafting progress bar (NEW FEATURE)
    const craftEl = document.getElementById('sorare-crafting');
    if (craftData && craftData.essenceBalance != null) {
        const bal = craftData.essenceBalance;
        const cost = craftData.craftingCost || 1000;
        const essPct = Math.min(100, Math.round((bal / cost) * 100));
        const essNeeded = Math.max(0, cost - bal);
        const essColor = essPct >= 100 ? '#4ade80' : '#a78bfa';
        let cHtml = '<div class="sorare-section-label">🔮 Crafting Progress</div>';
        cHtml += '<div class="sorare-lineup" style="padding:0.4rem 0.5rem;">';
        cHtml += '<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.2rem;">';
        cHtml += '<span style="font-size:0.55rem;color:rgba(255,255,255,0.7);">Essence</span>';
        cHtml += '<span style="font-size:0.55rem;font-weight:600;color:' + essColor + ';">' + bal.toLocaleString() + ' / ' + cost.toLocaleString() + '</span>';
        cHtml += '</div>';
        cHtml += '<div style="width:100%;height:6px;background:rgba(255,255,255,0.08);border-radius:3px;overflow:hidden;margin-bottom:0.15rem;">';
        cHtml += '<div style="width:' + essPct + '%;height:100%;background:' + essColor + ';border-radius:3px;transition:width 0.5s;"></div>';
        cHtml += '</div>';
        cHtml += '<div style="display:flex;justify-content:space-between;">';
        cHtml += '<span style="font-size:0.45rem;color:rgba(255,255,255,0.4);">' + essPct + '%</span>';
        if (essNeeded > 0) {
            cHtml += '<span style="font-size:0.45rem;color:rgba(255,255,255,0.4);">' + essNeeded + ' more needed</span>';
        } else {
            cHtml += '<span style="font-size:0.45rem;color:#4ade80;font-weight:600;">✓ Enough</span>';
        }
        cHtml += '</div></div>';
        craftEl.innerHTML = cHtml;
    } else {
        craftEl.innerHTML = '';
    }

    // ... rest of existing Sorare code ...
    if (!data || !data.activeFixture) return;
    const fix = data.activeFixture;
    // (rest of existing implementation stays the same)
}
`;

console.log("Mobile dashboard update patches ready!");
console.log("These enhanced functions sync mobile with desktop's best features:");
console.log("1. Mind state decisions log");
console.log("2. Ticker market status dots");
console.log("3. X neon emoji SVGs");
console.log("4. Sorare daily tasks & crafting progress");
