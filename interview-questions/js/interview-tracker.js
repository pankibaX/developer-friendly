/**
 * Technical Interview Tracker & Modal System
 * - 1-4 Answer Quality Rating per question (used internally for calculations)
 * - Automatic Calculation of Domain Proficiency & Hiring Recommendation (HIRE / REJECT)
 * - ZERO NUMBERS in the generated Management & HR report
 * - Qualitative explanations for each technology domain and assessed concept
 * - Code snippet popup modals with instant clipboard copying
 */

const STORAGE_KEY = 'interview_master_data_v7';

const TOPIC_REGISTRY = {
    'java':         { title: 'Core Java & JVM',           shortTitle: 'Core Java & JVM',     totalQuestions: 24, page: 'java.html',               icon: '☕' },
    'spring':       { title: 'Spring & Spring Boot',       shortTitle: 'Spring & Spring Boot', totalQuestions: 29, page: 'spring-spring-boot.html', icon: '🌱' },
    'batch':        { title: 'Spring Batch & Large-Scale Processing', shortTitle: 'Spring Batch', totalQuestions: 20, page: 'spring-batch.html', icon: '⚙️' },
    'orm':          { title: 'ORM, Hibernate & JPA',       shortTitle: 'ORM & Hibernate',      totalQuestions: 20,  page: 'orm-hibernate-jpa.html',  icon: '🗄️' },
    'rest':         { title: 'REST API & Microservices',   shortTitle: 'REST & Microservices', totalQuestions: 20,  page: 'rest-api-microservices.html', icon: '🌐' },
    'aws':          { title: 'AWS (Lambda & EC2)',         shortTitle: 'AWS Cloud',            totalQuestions: 20,  page: 'aws-deployment.html',     icon: '☁️' },
    'camel':        { title: 'Apache Camel & Integration', shortTitle: 'Apache Camel',         totalQuestions: 24,  page: 'camel.html',              icon: '🐪' },
    'kafka':        { title: 'Apache Kafka & Streaming',   shortTitle: 'Apache Kafka',         totalQuestions: 20,  page: 'kafka.html',              icon: '🦅' },
    'k8s':          { title: 'Kubernetes & Docker',        shortTitle: 'Kubernetes & Docker',  totalQuestions: 23,  page: 'kubernetes-docker.html',  icon: '🐳' },
    'angular':      { title: 'Angular (Modern)',           shortTitle: 'Angular',              totalQuestions: 20,  page: 'angular.html',            icon: '🅰️' },
    'architecture': { title: 'Architecture & Design',     shortTitle: 'Architecture & Design',totalQuestions: 22,  page: 'architecture-design.html',icon: '📐' },
    'python_core':      { title: 'Python Core & AsyncIO',      shortTitle: 'Python Core',          totalQuestions: 20, page: 'python-core.html',            icon: '🐍' },
    'python_frameworks':{ title: 'Django, FastAPI & Flask',    shortTitle: 'Django, FastAPI & Flask', totalQuestions: 20, page: 'python-web-frameworks.html', icon: '🚀' }
};

// 1-4 Rating Configuration (used internally for scoring)
const RATING_CONFIG = [
    { 
        val: 1, 
        label: 'Cannot Explain', 
        qualitative: 'Unsatisfactory (Unable to explain)', 
        color: 'active-1' 
    },
    { 
        val: 2, 
        label: 'Partial',         
        qualitative: 'Partial (Required hints)', 
        color: 'active-2' 
    },
    { 
        val: 3, 
        label: 'Good',            
        qualitative: 'Competent (Cleared cleanly)', 
        color: 'active-3' 
    },
    { 
        val: 4, 
        label: 'Expert',          
        qualitative: 'Strong (Exemplary depth)', 
        color: 'active-4' 
    }
];

// Calculated proficiency from internal average score
function calcProficiency(avgRating) {
    if (avgRating === null || avgRating === undefined) {
        return { 
            label: 'Not Evaluated', 
            badge: 'none', 
            evalText: 'No assessment recorded for this domain.' 
        };
    }
    if (avgRating >= 3.5) {
        return { 
            label: 'Expert',       
            badge: 'expert',        
            evalText: 'Demonstrates strong domain mastery; articulates low-level runtime mechanics and architectural trade-offs with confidence.' 
        };
    }
    if (avgRating >= 2.5) {
        return { 
            label: 'Advanced',     
            badge: 'advanced',      
            evalText: 'Solid engineering competence; solves production scenarios cleanly with minimal guidance.' 
        };
    }
    if (avgRating >= 1.5) {
        return { 
            label: 'Intermediate', 
            badge: 'intermediate',  
            evalText: 'Grasps core concepts and syntax, but requires prompting on concurrency, edge cases, and runtime troubleshooting.' 
        };
    }
    return { 
        label: 'Beginner',      
        badge: 'beginner',      
        evalText: 'Lacks required depth in core framework internals and runtime debugging.' 
    };
}

// Helper to format domain titles with natural grammar (e.g. "A", "A and B", "A, B, and C")
function formatDomainList(list) {
    if (!list || list.length === 0) return "";
    if (list.length === 1) return list[0];
    if (list.length === 2) return `${list[0]} and ${list[1]}`;
    return `${list.slice(0, -1).join(", ")}, and ${list[list.length - 1]}`;
}

// Automatic recommendation calculator based on assessed question performance and specific evaluated technologies
function calculateRecommendation(overallAvg, totalRatedCount, domainBreakdown = []) {
    if (totalRatedCount === 0) {
        return {
            verdictText: 'Awaiting Ratings',
            badgeClass: 'none',
            subText: 'Rate candidate responses across domains to generate recommendation',
            reportRecommendation: 'PENDING',
            executiveSummary: 'Assessment not yet started.'
        };
    }

    const assessedNames = domainBreakdown.map(d => d.title);
    const domainNamesFormatted = formatDomainList(assessedNames);
    const prep = assessedNames.length === 1 ? 'in' : 'across';

    if (totalRatedCount < 3) {
        return {
            verdictText: 'In Progress',
            badgeClass: 'intermediate',
            subText: 'Minimum 3 questions recommended for a reliable decision',
            reportRecommendation: 'INSUFFICIENT DATA',
            executiveSummary: assessedNames.length > 0 
                ? `Preliminary evaluation in progress for ${domainNamesFormatted} (minimum 3 questions recommended for a reliable hiring decision).`
                : 'Preliminary evaluation in progress (minimum 3 questions recommended for a reliable hiring decision).'
        };
    }

    const strongDomains = domainBreakdown.filter(d => d.avg >= 2.5).map(d => d.title);
    const strugglingDomains = domainBreakdown.filter(d => d.avg < 2.5).map(d => d.title);

    if (overallAvg >= 2.5) {
        let summary;
        if (assessedNames.length > 0) {
            summary = `Demonstrated solid hands-on competence and clear engineering judgment ${prep} ${domainNamesFormatted}. Recommended for hire against the senior engineering bar.`;
        } else {
            summary = 'Demonstrated solid hands-on competence and clear engineering judgment. Recommended for hire against the senior engineering bar.';
        }

        return {
            verdictText: '✅ HIRE',
            badgeClass: 'hire',
            subText: 'Meets Senior / Lead Engineering Bar',
            reportRecommendation: 'HIRE',
            executiveSummary: summary
        };
    }

    // REJECT outcome tailored to evaluated technologies
    let rejectSummary;
    if (strongDomains.length > 0 && strugglingDomains.length > 0) {
        const strongList = formatDomainList(strongDomains);
        const strugglingList = formatDomainList(strugglingDomains);
        const sPrep = strugglingDomains.length === 1 ? 'in' : 'across';
        rejectSummary = `Demonstrated working competence in ${strongList}, but showed critical gaps in core runtime mechanics and failure modes ${sPrep} ${strugglingList}. Does not meet the senior engineering bar.`;
    } else if (strugglingDomains.length > 0) {
        const strugglingList = formatDomainList(strugglingDomains);
        const sPrep = strugglingDomains.length === 1 ? 'in' : 'across';
        rejectSummary = `Did not demonstrate sufficient depth on core mechanics and failure modes ${sPrep} ${strugglingList}. Does not meet the senior engineering bar.`;
    } else if (assessedNames.length > 0) {
        rejectSummary = `Did not demonstrate sufficient depth on core mechanics and failure modes ${prep} ${domainNamesFormatted}. Does not meet the senior engineering bar.`;
    } else {
        rejectSummary = 'Did not demonstrate sufficient depth on core mechanics and failure modes. Does not meet the senior engineering bar.';
    }

    return {
        verdictText: '❌ REJECT',
        badgeClass: 'reject',
        subText: 'Falls below senior technical bar',
        reportRecommendation: 'REJECT',
        executiveSummary: rejectSummary
    };
}

/* ─────────────────────────────────────────────────────
   STORAGE HELPERS
───────────────────────────────────────────────────── */
function getAllData() {
    try {
        const s = localStorage.getItem(STORAGE_KEY);
        if (!s) return { topics: {} };
        const d = JSON.parse(s);
        if (!d.topics) d.topics = {};
        return d;
    } catch (e) { 
        return { topics: {} }; 
    }
}

function saveAllData(data) {
    try { 
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); 
    } catch (e) { 
        console.error('localStorage write error', e); 
    }
}

function getOrCreateTopic(data, topicKey) {
    if (!data.topics[topicKey]) {
        data.topics[topicKey] = { ratings: {} };
    }
    if (!data.topics[topicKey].ratings) data.topics[topicKey].ratings = {};
    return data.topics[topicKey];
}

/* ─────────────────────────────────────────────────────
   PER-QUESTION RATING (1-4)
───────────────────────────────────────────────────── */
function setQuestionRating(topicKey, qId, rating, conceptLabel) {
    const data = getAllData();
    const topic = getOrCreateTopic(data, topicKey);

    topic.ratings[qId] = { rating: parseInt(rating, 10), concept: conceptLabel, ts: Date.now() };
    saveAllData(data);

    updateQuestionRatingUI(qId, parseInt(rating, 10));
    updateTopicHeaderUI(topicKey);
}

function updateQuestionRatingUI(qId, activeRating) {
    const group = document.getElementById('star-group-' + qId);
    if (!group) return;

    group.querySelectorAll('.star-btn').forEach(btn => {
        const val = parseInt(btn.getAttribute('data-rating'), 10);
        btn.className = 'star-btn';
        if (val === activeRating) btn.classList.add('active-' + val);
    });

    const scoreDisplay = document.getElementById('q-score-' + qId);
    if (scoreDisplay) {
        const cfg = RATING_CONFIG.find(r => r.val === activeRating);
        if (cfg) {
            scoreDisplay.textContent = `Assessed: ${cfg.label}`;
            scoreDisplay.className = 'q-score-display scored';
        }
    }

    // Update card header status pill in accordion view
    const statusPill = document.getElementById('card-status-' + qId);
    if (statusPill) {
        const cfg = RATING_CONFIG.find(r => r.val === activeRating);
        if (cfg) {
            statusPill.textContent = `⭐ ${cfg.label} (${activeRating})`;
            statusPill.className = `card-status-pill rated-${activeRating}`;
        }
    }

    // Highlight card border based on assessment
    const card = document.getElementById('q-' + qId);
    if (card) {
        card.style.borderColor = activeRating >= 3 ? '#4ade80' : activeRating === 2 ? '#fb923c' : '#fca5a5';
    }

    updateSidebarProgress();
}

function getDomainTotalQuestions(topicKey) {
    const cards = document.querySelectorAll('.question-card');
    if (cards && cards.length > 0) {
        try {
            const counts = JSON.parse(localStorage.getItem('interview_dynamic_counts') || '{}');
            counts[topicKey] = cards.length;
            localStorage.setItem('interview_dynamic_counts', JSON.stringify(counts));
        } catch (e) {}
        return cards.length;
    }
    try {
        const counts = JSON.parse(localStorage.getItem('interview_dynamic_counts') || '{}');
        if (counts[topicKey]) return counts[topicKey];
    } catch (e) {}
    if (window.COVERAGE_MATRIX && window.COVERAGE_MATRIX.domains && window.COVERAGE_MATRIX.domains[topicKey]) {
        return window.COVERAGE_MATRIX.domains[topicKey].totalEvaluatedQuestions;
    }
    return TOPIC_REGISTRY[topicKey]?.totalQuestions || 20;
}

function updateTopicHeaderUI(topicKey) {
    const data = getAllData();
    const topic = data.topics[topicKey] || { ratings: {} };
    const ratings = Object.values(topic.ratings || {}).map(r => r.rating);

    const count = ratings.length;
    const total = getDomainTotalQuestions(topicKey);

    const avg = count > 0 ? ratings.reduce((a, b) => a + b, 0) / count : null;
    const prof = calcProficiency(avg);

    const countEl = document.getElementById('statEvaluatedCount');
    if (countEl) {
        countEl.textContent = `${count} of ${total} Questions Rated`;
    }

    const verdictEl = document.getElementById('statVerdict');
    if (verdictEl) {
        verdictEl.className = 'verdict-badge ' + prof.badge;
        verdictEl.textContent = prof.label;
    }
}

/* ─────────────────────────────────────────────────────
   TOPIC PAGE INITIALIZATION & NAVIGATION SHORTCUTS
───────────────────────────────────────────────────── */
function scrollToQuestion(qId) {
    const card = document.getElementById('q-' + qId);
    if (card) {
        card.classList.add('expanded');
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        card.classList.remove('highlight-pulse');
        void card.offsetWidth;
        card.classList.add('highlight-pulse');
    }
}

function expandAllQuestions() {
    document.querySelectorAll('.question-card').forEach(c => c.classList.add('expanded'));
}

function collapseAllQuestions() {
    document.querySelectorAll('.question-card').forEach(c => c.classList.remove('expanded'));
}

function initGuidelinesBox() {
    const box = document.querySelector('.guideline-box');
    if (!box || box.querySelector('.guideline-box-header')) return;

    const titleEl = box.querySelector('h3');
    const titleText = titleEl ? titleEl.textContent : 'How to Conduct This Interview';
    const bodyHtml = box.querySelector('p')?.outerHTML || (box.querySelector('div:last-child')?.innerHTML || '');

    box.innerHTML = `
        <div class="guideline-box-header">
            <div class="guideline-box-title">
                <span>💡</span>
                <span>${titleText}</span>
            </div>
            <span class="guideline-box-toggle">Click to show instructions ▾</span>
        </div>
        <div class="guideline-box-body">
            ${bodyHtml}
        </div>
    `;

    box.onclick = (e) => {
        if (e.target.closest('a, button')) return;
        box.classList.toggle('open');
        const toggle = box.querySelector('.guideline-box-toggle');
        if (toggle) {
            toggle.textContent = box.classList.contains('open') ? 'Hide instructions ▴' : 'Click to show instructions ▾';
        }
    };
}

function initFilterBarControls() {
    const filterBar = document.querySelector('.filter-bar');
    if (!filterBar || filterBar.querySelector('.filter-actions')) return;

    const actions = document.createElement('div');
    actions.className = 'filter-actions';
    actions.innerHTML = `
        <button type="button" class="btn-outline btn-xs" onclick="expandAllQuestions()" title="Expand all question cards">📂 Expand All</button>
        <button type="button" class="btn-outline btn-xs" onclick="collapseAllQuestions()" title="Collapse all question cards">📁 Collapse All</button>
    `;
    filterBar.appendChild(actions);

    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.onkeyup = () => {
            const query = searchInput.value.toLowerCase().trim();
            const cards = document.querySelectorAll('.question-card');
            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                const keywords = card.getAttribute('data-keywords') || '';
                if (!query) {
                    card.style.display = 'block';
                } else if (text.includes(query) || keywords.includes(query)) {
                    card.style.display = 'block';
                    card.classList.add('expanded');
                } else {
                    card.style.display = 'none';
                }
            });
        };
    }
}

function updateSidebarProgress() {
    const data = getAllData();
    let grandRated = 0;
    let grandTotal = 0;

    for (const [key, meta] of Object.entries(TOPIC_REGISTRY)) {
        const topic = data.topics[key] || { ratings: {} };
        const ratedCount = Object.keys(topic.ratings || {}).length;
        const total = meta.totalQuestions || 20;
        grandRated += ratedCount;
        grandTotal += total;

        const link = document.querySelector(`.nav-link[href="${meta.page}"]`);
        if (link) {
            let badge = link.querySelector('.nav-badge');
            if (!badge) {
                badge = document.createElement('span');
                link.appendChild(badge);
            }
            if (ratedCount > 0) {
                badge.textContent = `${ratedCount}/${total}`;
                badge.className = 'nav-badge rated';
            } else {
                badge.textContent = `${total}`;
                badge.className = 'nav-badge';
            }
            badge.style.display = 'inline-block';
        }
    }

    // Update Sidebar Live Assessment Mini Card (if present)
    const miniCount = document.getElementById('sidebarMiniCount');
    const miniFill  = document.getElementById('sidebarMiniFill');
    const miniStatus = document.getElementById('sidebarMiniStatus');
    if (miniCount) miniCount.textContent = `${grandRated}/${grandTotal} Rated`;
    if (miniFill) {
        const pct = grandTotal > 0 ? Math.min(100, Math.round((grandRated / grandTotal) * 100)) : 0;
        miniFill.style.width = pct + '%';
    }
    if (miniStatus) {
        if (grandRated === 0) {
            miniStatus.textContent = 'Awaiting Assessment';
            miniStatus.style.color = 'var(--text-muted)';
        } else {
            const overall = calcProficiency(grandRated > 0 ? getOverallAverageScore(data) : null);
            miniStatus.textContent = overall.label;
            miniStatus.style.color = overall.badge === 'expert' || overall.badge === 'advanced' ? '#16a34a' : (overall.badge === 'intermediate' ? '#2563eb' : '#d97706');
        }
    }
}

function getOverallAverageScore(data) {
    let totalScore = 0;
    let totalRatings = 0;
    for (const topic of Object.values(data.topics || {})) {
        for (const item of Object.values(topic.ratings || {})) {
            if (item && item.score) {
                totalScore += item.score;
                totalRatings++;
            }
        }
    }
    return totalRatings > 0 ? (totalScore / totalRatings) : null;
}

function filterSidebarTopics(query) {
    query = (query || '').toLowerCase().trim();
    const items = document.querySelectorAll('.nav-links > li');
    const headerGroups = [];

    items.forEach(li => {
        if (li.classList.contains('nav-section-title')) {
            headerGroups.push({ header: li, visibleCount: 0 });
        } else {
            const link = li.querySelector('.nav-link');
            if (!link) return;
            const text = link.textContent.toLowerCase();
            if (!query || text.includes(query)) {
                li.style.display = 'block';
                if (headerGroups.length > 0) {
                    headerGroups[headerGroups.length - 1].visibleCount++;
                }
            } else {
                li.style.display = 'none';
            }
        }
    });

    headerGroups.forEach(group => {
        group.header.style.display = (group.visibleCount > 0 || !query) ? 'block' : 'none';
    });
}

function initBackToTop() {
    let btn = document.getElementById('backToTopBtn');
    if (!btn) {
        btn = document.createElement('button');
        btn.id = 'backToTopBtn';
        btn.className = 'back-to-top-btn';
        btn.innerHTML = '▲';
        btn.setAttribute('aria-label', 'Scroll back to top');
        btn.title = 'Back to top of questions';
        btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
        document.body.appendChild(btn);
    }
    window.addEventListener('scroll', () => {
        if (window.scrollY > 350) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    });
}

function syncDynamicQuestionUI(topicKey) {
    const cards = document.querySelectorAll('.question-card');
    if (!cards || cards.length === 0) return;

    // Remove quick jump navigator if present in DOM
    const existingJump = document.querySelector('.quick-jump-container');
    if (existingJump) {
        existingJump.remove();
    }

    cards.forEach((card, idx) => {
        const qIdMatch = card.id ? card.id.match(/^q-(\d+)$/) : null;
        const qId = qIdMatch ? parseInt(qIdMatch[1], 10) : (idx + 1);
        if (!card.id) card.id = 'q-' + qId;

        const badgeEl = card.querySelector('.concept-badge');
        const badgeText = badgeEl ? badgeEl.textContent.trim() : `Topic ${qId}`;

        // Extract concise question preview
        let previewTitle = '';
        const qTitleEl = card.querySelector('.question-title');
        if (qTitleEl) {
            const firstSentence = qTitleEl.textContent.replace(/\s+/g, ' ').trim().split('.')[0];
            previewTitle = firstSentence.length > 70 ? firstSentence.substring(0, 67) + '...' : firstSentence;
        } else {
            previewTitle = badgeText;
        }

        // Rebuild card header into sleek accordion header
        const cardHeader = card.querySelector('.card-header');
        if (cardHeader && !cardHeader.querySelector('.card-header-left')) {
            cardHeader.innerHTML = `
                <div class="card-header-left">
                    <span class="q-num-pill">Q${qId}</span>
                    <span class="concept-badge">${badgeText}</span>
                    <span class="q-preview-title" title="${previewTitle.replace(/"/g, '&quot;')}">${previewTitle}</span>
                </div>
                <div class="card-header-right">
                    <span class="card-status-pill" id="card-status-${qId}">⚪ Not Rated</span>
                    <span class="accordion-chevron">▼</span>
                </div>
            `;
            cardHeader.onclick = (e) => {
                if (e.target.closest('button, a, select, input')) return;
                card.classList.toggle('expanded');
            };
        }
    });

    initFilterBarControls();
    initGuidelinesBox();
    updateSidebarProgress();
}

function renderStickyBreadcrumbAndSwitcher(topicKey) {
    const evalBar = document.querySelector('.skill-evaluation-bar');
    if (!evalBar) return;

    if (evalBar.querySelector('.sticky-nav-strip')) return; // Avoid duplicates

    const meta = TOPIC_REGISTRY[topicKey] || { title: topicKey, icon: '📌', page: '#' };

    const strip = document.createElement('div');
    strip.className = 'sticky-nav-strip';

    // Build options for all domains
    let optionsHtml = '';
    for (const [key, tMeta] of Object.entries(TOPIC_REGISTRY)) {
        const selected = (key === topicKey) ? 'selected' : '';
        optionsHtml += `<option value="${tMeta.page}" ${selected}>${tMeta.icon} ${tMeta.title}</option>`;
    }

    strip.innerHTML = `
        <div class="breadcrumb-container">
            <a href="index.html" class="breadcrumb-home" title="Go to Master Summary Dashboard">
                <span>🏠</span> <strong>Master Hub</strong>
            </a>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">${meta.icon} ${meta.title}</span>
        </div>
        <div class="domain-quick-switcher">
            <label for="trackSwitcher" class="switcher-label">🔀 Switch Track:</label>
            <select id="trackSwitcher" class="track-select" onchange="if(this.value) window.location.href=this.value" aria-label="Switch Interview Domain">
                ${optionsHtml}
            </select>
            <a href="index.html" class="btn-back-hub" title="Return to Overview & Master Summary">
                <span>←</span> Back to Hub
            </a>
        </div>
    `;

    // Insert as the very first child of the sticky skill-evaluation-bar
    evalBar.insertBefore(strip, evalBar.firstChild);
}

function initTopicPage(topicKey) {
    window.currentTopicKey = topicKey;
    const data = getAllData();

    renderStickyBreadcrumbAndSwitcher(topicKey);
    syncDynamicQuestionUI(topicKey);

    const topic = data.topics[topicKey] || { ratings: {} };
    for (const [qId, item] of Object.entries(topic.ratings || {})) {
        updateQuestionRatingUI(parseInt(qId, 10), item.rating);
    }

    updateTopicHeaderUI(topicKey);
    initBackToTop();
    checkRefreshAndPromptEvaluationState();
}

function resetSkillData(topicKey) {
    const meta = TOPIC_REGISTRY[topicKey] || { title: topicKey };
    if (!confirm(`Reset all ratings for "${meta.title}"?`)) return;

    const data = getAllData();
    data.topics[topicKey] = { ratings: {} };
    saveAllData(data);

    // Reset star buttons on page
    document.querySelectorAll('.star-btn').forEach(b => b.className = 'star-btn');
    document.querySelectorAll('.q-score-display').forEach(el => {
        el.textContent = 'Not Rated';
        el.className = 'q-score-display';
    });
    document.querySelectorAll('.card-status-pill').forEach(el => {
        el.textContent = '⚪ Not Rated';
        el.className = 'card-status-pill';
    });
    document.querySelectorAll('.question-card').forEach(c => c.style.borderColor = '');

    updateTopicHeaderUI(topicKey);
    updateSidebarProgress();
}

/* ─────────────────────────────────────────────────────
   CODE SNIPPET POPUP MODAL
───────────────────────────────────────────────────── */
function openCodeSnippetModal(snippetId, titleText) {
    const raw = document.getElementById('snippet-' + snippetId);
    if (!raw) return;
    const code = (raw.innerText || raw.textContent).trim();
    const titleEl = document.getElementById('codeModalTitle');
    const preEl   = document.getElementById('codeModalPre');
    if (titleEl) titleEl.innerHTML = '💻 ' + (titleText || 'Code Challenge');
    if (preEl)   preEl.textContent = code;
    const modal = document.getElementById('codeModal') || document.getElementById('codeSnippetModal');
    if (modal) modal.classList.add('show');
}

function closeCodeSnippetModal() {
    const modal = document.getElementById('codeModal') || document.getElementById('codeSnippetModal');
    if (modal) modal.classList.remove('show');
}

function copyModalCode() {
    const preEl = document.getElementById('codeModalPre');
    if (!preEl) return;
    navigator.clipboard.writeText(preEl.textContent).then(() => {
        const btn = document.getElementById('copyCodeBtn');
        if (btn) {
            const orig = btn.textContent;
            btn.textContent = '✅ Copied!';
            setTimeout(() => btn.textContent = orig, 2000);
        }
    });
}

/* ─────────────────────────────────────────────────────
   SOLUTION & CANDIDATE EVALUATION POPUP MODAL
───────────────────────────────────────────────────── */
function openSolutionModal(qNum) {
    const card = document.getElementById('q-' + qNum);
    if (!card) return;

    const badge = card.querySelector('.concept-badge')?.textContent || 'Solution & Explanation';
    const qNumber = card.querySelector('.q-number')?.textContent || ('Question ' + qNum);
    const solutionContent = card.querySelector('.solution-content');
    if (!solutionContent) return;

    // Ensure solutionModal element exists in DOM (dynamic injection if absent)
    let modal = document.getElementById('solutionModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'solutionModal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-card modal-solution-card">
                <div class="modal-header">
                    <div>
                        <span class="concept-badge" id="solutionModalBadge" style="margin-bottom: 4px; display: inline-block;"></span>
                        <h3 id="solutionModalTitle" style="margin: 0; font-size: 16px;">👁️ Solution & Candidate Evaluation</h3>
                    </div>
                    <button class="btn-outline" onclick="closeSolutionModal()" style="padding: 4px 10px;">✕</button>
                </div>
                <div class="modal-body" id="solutionModalBody"></div>
                <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <span style="font-size: 12px; color: var(--text-muted);">💡 Tip: Rate candidate below on the question card</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn-outline" id="copySolutionCodeBtn" onclick="copySolutionCode()" style="display: none;">📋 Copy Solution Code</button>
                        <button class="btn-primary" onclick="closeSolutionModal()">Close</button>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(modal);
    }

    const titleEl = document.getElementById('solutionModalTitle');
    const badgeEl = document.getElementById('solutionModalBadge');
    const bodyEl  = document.getElementById('solutionModalBody');
    const copyBtn = document.getElementById('copySolutionCodeBtn');

    if (titleEl) titleEl.textContent = `👁️ ${qNumber}: Solution & Candidate Evaluation`;
    if (badgeEl) badgeEl.textContent = badge;

    if (bodyEl) {
        bodyEl.innerHTML = solutionContent.innerHTML;
        // Check for code block inside solution to enable copy button
        const codeBlock = bodyEl.querySelector('pre code');
        if (copyBtn) {
            if (codeBlock) {
                copyBtn.style.display = 'inline-flex';
                copyBtn.setAttribute('data-code', codeBlock.textContent);
            } else {
                copyBtn.style.display = 'none';
            }
        }
    }

    modal.classList.add('show');
}

function closeSolutionModal() {
    const modal = document.getElementById('solutionModal');
    if (modal) modal.classList.remove('show');
}

function copySolutionCode() {
    const btn = document.getElementById('copySolutionCodeBtn');
    if (!btn) return;
    const code = btn.getAttribute('data-code') || '';
    if (!code) return;
    navigator.clipboard.writeText(code).then(() => {
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => btn.textContent = orig, 2000);
    });
}

// Global Modal Keyboard & Outside Click Listeners
window.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCodeSnippetModal();
        closeSolutionModal();
        closeMasterSummaryModal();
        closeRefreshPromptModal();
    }
});

window.addEventListener('click', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('modal-overlay')) {
        closeCodeSnippetModal();
        closeSolutionModal();
        closeMasterSummaryModal();
        closeRefreshPromptModal();
    }
});

/* ─────────────────────────────────────────────────────
   MASTER SCORECARD (index.html)
───────────────────────────────────────────────────── */
function initIndexPage() {
    renderMasterScorecard();
    initGuidelinesBox();
    updateSidebarProgress();
    checkRefreshAndPromptEvaluationState();
}

function renderMasterScorecard() {
    const data = getAllData();

    let grandCount = 0;
    const tableBody = document.getElementById('masterSummaryTableBody');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    let allRatings = [];
    let domainBreakdown = [];

    for (const [key, meta] of Object.entries(TOPIC_REGISTRY)) {
        const topic   = data.topics[key] || { ratings: {} };
        const ratings = Object.values(topic.ratings || {}).map(r => r.rating);
        const count   = ratings.length;
        grandCount   += count;

        ratings.forEach(r => allRatings.push(r));

        const avg  = count > 0 ? ratings.reduce((a, b) => a + b, 0) / count : null;
        const prof = calcProficiency(avg);

        if (count > 0) {
            domainBreakdown.push({
                key,
                title: meta.shortTitle || meta.title,
                avg,
                count
            });
        }

        const totalQuestions = getDomainTotalQuestions(key);
        const countCell = `${count} of ${totalQuestions} questions`;
        const avgCell   = avg !== null ? `<strong>${avg.toFixed(1)}</strong> / 4` : '<span style="color:#94a3b8">—</span>';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${meta.icon} ${meta.title}</strong></td>
            <td>${countCell}</td>
            <td style="text-align:center;">${avgCell}</td>
            <td><span class="verdict-badge ${prof.badge}">${prof.label}</span></td>
            <td><a href="${meta.page}" class="btn-outline" style="padding: 4px 10px; font-size: 12px;">Open Section →</a></td>
        `;
        tableBody.appendChild(row);
    }

    const totalEl = document.getElementById('masterTotalEvaluated');
    if (totalEl) totalEl.textContent = `${grandCount} Questions Assessed`;

    // Calculate overall metrics
    const overallAvg = allRatings.length > 0 ? (allRatings.reduce((a, b) => a + b, 0) / allRatings.length) : null;
    const overallProf = calcProficiency(overallAvg);

    // Update Overall Calculated Proficiency card
    const overallBadge = document.getElementById('masterOverallVerdict');
    if (overallBadge) {
        overallBadge.className = 'verdict-badge ' + overallProf.badge;
        overallBadge.textContent = overallProf.label;
    }

    // Update Calculated Recommendation card
    const rec = calculateRecommendation(overallAvg, grandCount, domainBreakdown);
    const recBadge = document.getElementById('masterCalculatedRecommendation');
    const recSub = document.getElementById('masterRecommendationSub');

    if (recBadge) {
        recBadge.className = 'verdict-badge ' + rec.badgeClass;
        recBadge.textContent = rec.verdictText;
    }
    if (recSub) {
        recSub.textContent = rec.subText;
    }
}

/* ─────────────────────────────────────────────────────
   MASTER SUMMARY REPORT GENERATOR (FOR MANAGEMENT / HR)
   STRICT REQUIREMENT: ZERO NUMBERS IN THE REPORT TEXT
───────────────────────────────────────────────────── */
function generateFeedbackReportText() {
    const data = getAllData();
    let hasData = false;
    let skillBlocks = [];
    let allRatings = [];
    let domainBreakdown = [];

    for (const [key, meta] of Object.entries(TOPIC_REGISTRY)) {
        const topic   = data.topics[key] || { ratings: {} };
        const entries = Object.entries(topic.ratings || {});
        if (entries.length === 0) continue;

        hasData = true;
        const ratings = entries.map(([, v]) => v.rating);
        allRatings.push(...ratings);

        const avg  = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        const prof = calcProficiency(avg);

        domainBreakdown.push({
            key,
            title: meta.shortTitle || meta.title,
            avg,
            prof
        });

        // Sort by question ID for consistent ordering
        entries.sort((a, b) => parseInt(a[0], 10) - parseInt(b[0], 10));

        // Format technology block (structured yet natural engineering feedback)
        let block = `• ${meta.shortTitle}: ${prof.label}\n`;
        block += `  Domain Notes: ${prof.evalText}\n`;
        block += `  Evaluated Areas:\n`;

        entries.forEach(([, item]) => {
            const rCfg = RATING_CONFIG.find(r => r.val === item.rating);
            const qual = rCfg ? rCfg.qualitative : 'Assessed';
            block += `  - ${item.concept}: ${qual}\n`;
        });

        skillBlocks.push(block);
    }

    if (!hasData) return null;

    const overallAvg = allRatings.reduce((a, b) => a + b, 0) / allRatings.length;
    const overallProf = calcProficiency(overallAvg);
    const rec = calculateRecommendation(overallAvg, allRatings.length, domainBreakdown);

    // Build the structured report (10-20% platform/system feel, 80-90% authentic human engineering judgment)
    let report = `TECHNICAL EVALUATION REPORT\n`;
    report += `===========================\n`;
    report += `Date: ${new Date().toLocaleDateString()}\n`;
    report += `Recommendation: ${rec.reportRecommendation}\n\n`;

    report += `SUMMARY\n`;
    report += `───────\n`;
    report += `Overall Assessment: ${overallProf.label}\n`;
    report += `Evaluation Notes: ${rec.executiveSummary}\n\n`;

    report += `TECHNICAL BREAKDOWN BY DOMAIN\n`;
    report += `─────────────────────────────\n`;
    report += skillBlocks.join('\n') + '\n';

    return report;
}

function downloadFeedbackReportText(filename) {
    const report = generateFeedbackReportText();
    if (!report) {
        alert('No questions have been assessed yet. Please rate candidate answers in any section first.');
        return;
    }
    const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const dateStr = new Date().toISOString().slice(0, 10);
    a.href = url;
    a.download = filename || `Technical-Evaluation-Feedback-${dateStr}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function ensureMasterSummaryModal() {
    let modal = document.getElementById('masterSummaryModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'masterSummaryModal';
        modal.innerHTML = `
            <div class="modal-card" style="max-width: 750px;">
                <div class="modal-header">
                    <h3>📋 Technical Evaluation Feedback Report</h3>
                    <button class="btn-outline" onclick="closeMasterSummaryModal()" style="padding: 4px 10px;">✕</button>
                </div>
                <div class="modal-body">
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 12px;">
                        Copy or download this evaluation feedback report for hiring review:
                    </p>
                    <textarea id="masterSummaryTextarea" readonly style="width: 100%; height: 320px; font-family: 'JetBrains Mono', monospace; font-size: 12px; padding: 14px; border: 1px solid var(--border-color); border-radius: 6px; background-color: #f8fafc; resize: vertical; line-height: 1.5;"></textarea>
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap;">
                    <button class="btn-outline" onclick="closeMasterSummaryModal()">Close</button>
                    <button class="btn-outline" id="downloadMasterSummaryBtn" onclick="downloadFeedbackReportText()" style="display: inline-flex; align-items: center; gap: 6px;">📥 Download Report (.txt)</button>
                    <button class="btn-primary" id="copyMasterSummaryBtn" onclick="copyMasterSummaryToClipboard()">📋 Copy Report to Clipboard</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    return modal;
}

function openMasterSummaryModal() {
    const report = generateFeedbackReportText();
    if (!report) {
        alert('No questions have been assessed yet. Please rate candidate answers in any section (e.g. Java, Spring) first.');
        return;
    }

    const modal = ensureMasterSummaryModal();
    const ta = document.getElementById('masterSummaryTextarea');
    if (ta) ta.value = report;
    if (modal) modal.classList.add('show');
}

function closeMasterSummaryModal() {
    const modal = document.getElementById('masterSummaryModal');
    if (modal) modal.classList.remove('show');
}

function copyMasterSummaryToClipboard() {
    const ta = document.getElementById('masterSummaryTextarea');
    if (!ta) return;
    ta.select();
    navigator.clipboard.writeText(ta.value).then(() => {
        const btn = document.getElementById('copyMasterSummaryBtn');
        const orig = btn.textContent;
        btn.textContent = '✅ Copied to Clipboard!';
        setTimeout(() => btn.textContent = orig, 2000);
    });
}

/* ─────────────────────────────────────────────────────
   SESSION RESTORE & ON-REFRESH PROMPT
   Detects browser reload and prompts user: "Need to save or continue?"
───────────────────────────────────────────────────── */
function isPageRefreshed() {
    try {
        const navEntries = performance.getEntriesByType('navigation');
        if (navEntries && navEntries.length > 0) {
            return navEntries[0].type === 'reload';
        }
        if (window.performance && window.performance.navigation) {
            return window.performance.navigation.type === 1; // 1 = TYPE_RELOAD
        }
    } catch (e) {
        console.warn('Navigation timing check error:', e);
    }
    return false;
}

function getTotalEvaluatedCount() {
    const data = getAllData();
    let count = 0;
    if (data && data.topics) {
        for (const topic of Object.values(data.topics)) {
            if (topic && topic.ratings) {
                count += Object.keys(topic.ratings).length;
            }
        }
    }
    return count;
}

function checkRefreshAndPromptEvaluationState() {
    const isReload = isPageRefreshed();
    const count = getTotalEvaluatedCount();

    if (isReload && count > 0) {
        // Brief timeout ensures existing ratings have rendered visually underneath
        setTimeout(() => {
            showRefreshPromptModal();
        }, 150);
    }
}

function ensureRefreshPromptModal() {
    let modal = document.getElementById('refreshSessionPromptModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.id = 'refreshSessionPromptModal';
        modal.innerHTML = `
            <div class="modal-card" style="max-width: 540px; text-align: left;">
                <div class="modal-header" style="border-bottom: 1px solid var(--border-color); padding: 16px 20px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 26px;">📋</span>
                        <div>
                            <h3 style="margin: 0; font-size: 16px; color: var(--text-primary); font-weight: 700;">Existing Evaluation Data Detected</h3>
                            <span style="font-size: 12px; color: var(--text-secondary);">Active candidate assessment found in browser storage</span>
                        </div>
                    </div>
                    <button class="btn-outline" onclick="closeRefreshPromptModal()" style="padding: 4px 10px;" title="Dismiss & Continue">✕</button>
                </div>
                <div class="modal-body" style="padding: 18px 20px;">
                    <div id="refreshPromptStats" style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; margin-bottom: 16px;">
                    </div>
                    <p style="font-size: 13.5px; color: var(--text-primary); line-height: 1.5; margin: 0;">
                        Do you need to <strong>Save / Export</strong> the evaluation report or <strong>Continue</strong> your assessment session?
                    </p>
                </div>
                <div class="modal-footer" style="display: flex; gap: 10px; justify-content: flex-end; flex-wrap: wrap; border-top: 1px solid var(--border-color); padding: 14px 20px;">
                    <button class="btn-outline" onclick="resetFromRefreshPrompt()" style="color: #ef4444; border-color: #fca5a5; margin-right: auto;" title="Clear all ratings and start fresh">
                        🔄 Start Fresh
                    </button>
                    <button class="btn-primary" onclick="saveFromRefreshPrompt()" style="background-color: #059669; border-color: #059669; display: inline-flex; align-items: center; gap: 6px;">
                        <span>💾</span> Save / Export Report
                    </button>
                    <button class="btn-outline" onclick="continueFromRefreshPrompt()" style="display: inline-flex; align-items: center; gap: 6px; font-weight: 600;">
                        <span>▶️</span> Continue Evaluation
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    return modal;
}

function updateRefreshPromptStats() {
    const container = document.getElementById('refreshPromptStats');
    if (!container) return;

    const data = getAllData();
    let totalRatings = 0;
    const activeDomains = [];

    for (const [key, meta] of Object.entries(TOPIC_REGISTRY)) {
        const topic = data.topics[key];
        if (topic && topic.ratings) {
            const count = Object.keys(topic.ratings).length;
            if (count > 0) {
                totalRatings += count;
                activeDomains.push({
                    title: meta.shortTitle || meta.title,
                    icon: meta.icon || '📌',
                    count
                });
            }
        }
    }

    if (totalRatings === 0) {
        container.innerHTML = `<span style="font-size: 13px; color: var(--text-secondary);">No active ratings found.</span>`;
        return;
    }

    const domainPills = activeDomains.map(d =>
        `<span style="display: inline-block; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px 8px; font-size: 11px; margin: 2px 4px 2px 0;">${d.icon} ${d.title} (<strong>${d.count}</strong>)</span>`
    ).join('');

    container.innerHTML = `
        <div style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
            📊 <strong>${totalRatings}</strong> candidate responses evaluated across <strong>${activeDomains.length}</strong> topic${activeDomains.length > 1 ? 's' : ''}:
        </div>
        <div style="line-height: 1.6;">${domainPills}</div>
    `;
}

function showRefreshPromptModal() {
    ensureRefreshPromptModal();
    updateRefreshPromptStats();
    const modal = document.getElementById('refreshSessionPromptModal');
    if (modal) modal.classList.add('show');
}

function closeRefreshPromptModal() {
    const modal = document.getElementById('refreshSessionPromptModal');
    if (modal) modal.classList.remove('show');
}

function continueFromRefreshPrompt() {
    closeRefreshPromptModal();
}

function saveFromRefreshPrompt() {
    closeRefreshPromptModal();
    openMasterSummaryModal();
}

function resetFromRefreshPrompt() {
    if (confirm('Discard all active candidate evaluations and start fresh? This cannot be undone.')) {
        closeRefreshPromptModal();
        localStorage.removeItem(STORAGE_KEY);
        if (typeof renderMasterScorecard === 'function') renderMasterScorecard();
        if (window.currentTopicKey) {
            document.querySelectorAll('.star-btn').forEach(b => b.className = 'star-btn');
            document.querySelectorAll('.q-score-display').forEach(el => {
                el.textContent = 'Not Rated';
                el.className = 'q-score-display';
            });
            document.querySelectorAll('.card-status-pill').forEach(el => {
                el.textContent = '⚪ Not Rated';
                el.className = 'card-status-pill';
            });
            document.querySelectorAll('.question-card').forEach(c => c.style.borderColor = '');
            updateTopicHeaderUI(window.currentTopicKey);
        }
        updateSidebarProgress();
    }
}

function resetAllInterviewData() {
    if (confirm('Reset ALL candidate evaluations across ALL sections?')) {
        localStorage.removeItem(STORAGE_KEY);
        if (typeof renderMasterScorecard === 'function') renderMasterScorecard();
        if (window.currentTopicKey) {
            document.querySelectorAll('.star-btn').forEach(b => b.className = 'star-btn');
            document.querySelectorAll('.q-score-display').forEach(el => {
                el.textContent = 'Not Rated';
                el.className = 'q-score-display';
            });
            document.querySelectorAll('.card-status-pill').forEach(el => {
                el.textContent = '⚪ Not Rated';
                el.className = 'card-status-pill';
            });
            document.querySelectorAll('.question-card').forEach(c => c.style.borderColor = '');
            updateTopicHeaderUI(window.currentTopicKey);
        }
        updateSidebarProgress();
    }
}
