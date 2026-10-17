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
    'java':         { title: 'Core Java & JVM',           shortTitle: 'Core Java & JVM',     totalQuestions: 20, page: 'java.html',               icon: '☕' },
    'spring':       { title: 'Spring & Spring Boot',       shortTitle: 'Spring & Spring Boot', totalQuestions: 21, page: 'spring-spring-boot.html', icon: '🌱' },
    'orm':          { title: 'ORM, Hibernate & JPA',       shortTitle: 'ORM & Hibernate',      totalQuestions: 20,  page: 'orm-hibernate-jpa.html',  icon: '🗄️' },
    'rest':         { title: 'REST API & Microservices',   shortTitle: 'REST & Microservices', totalQuestions: 20,  page: 'rest-api-microservices.html', icon: '🌐' },
    'aws':          { title: 'AWS (Lambda & EC2)',         shortTitle: 'AWS Cloud',            totalQuestions: 20,  page: 'aws-deployment.html',     icon: '☁️' },
    'angular':      { title: 'Angular (Modern)',           shortTitle: 'Angular',              totalQuestions: 20,  page: 'angular.html',            icon: '🅰️' },
    'architecture': { title: 'Architecture & Design',     shortTitle: 'Architecture & Design',totalQuestions: 20,  page: 'architecture-design.html',icon: '📐' },
    'python_core':      { title: 'Python Core & AsyncIO',      shortTitle: 'Python Core',          totalQuestions: 20, page: 'python-core.html',            icon: '🐍' },
    'python_frameworks':{ title: 'Django, FastAPI & Flask',    shortTitle: 'Django, FastAPI & Flask', totalQuestions: 20, page: 'python-web-frameworks.html', icon: '🚀' }
};

// 1-4 Rating Configuration (used internally for scoring)
const RATING_CONFIG = [
    { 
        val: 1, 
        label: 'Cannot Explain', 
        qualitative: 'Critical Gap (Unable to Diagnose)', 
        color: 'active-1' 
    },
    { 
        val: 2, 
        label: 'Partial',         
        qualitative: 'Partial Understanding (Needed Guidance)', 
        color: 'active-2' 
    },
    { 
        val: 3, 
        label: 'Good',            
        qualitative: 'Good Comprehension', 
        color: 'active-3' 
    },
    { 
        val: 4, 
        label: 'Expert',          
        qualitative: 'Strong Mastery', 
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
            evalText: 'Demonstrates deep systems-level mastery of runtime architecture, low-level mechanics, and complex trade-offs with zero guidance required.' 
        };
    }
    if (avgRating >= 2.5) {
        return { 
            label: 'Advanced',     
            badge: 'advanced',      
            evalText: 'Solid practical engineering competence. Accurately diagnoses root causes, writes clean idiomatic solutions, and understands operational trade-offs.' 
        };
    }
    if (avgRating >= 1.5) {
        return { 
            label: 'Intermediate', 
            badge: 'intermediate',  
            evalText: 'Understands fundamental syntax and standard patterns, but shows difficulty with concurrency, memory models, or edge-case failure modes without prompting.' 
        };
    }
    return { 
        label: 'Beginner',      
        badge: 'beginner',      
        evalText: 'Basic conceptual familiarity only; struggled with debugging runtime failure modes, core contracts, and production edge cases.' 
    };
}

// Automatic recommendation calculator based on assessed question performance
function calculateRecommendation(overallAvg, totalRatedCount) {
    if (totalRatedCount === 0) {
        return {
            verdictText: 'Awaiting Ratings',
            badgeClass: 'none',
            subText: 'Rate candidate responses across domains to generate recommendation',
            reportRecommendation: 'PENDING EVALUATION',
            executiveSummary: 'Evaluation has not yet started. Please rate candidate answers across interview topics.'
        };
    }
    if (totalRatedCount < 3) {
        return {
            verdictText: 'In Progress',
            badgeClass: 'intermediate',
            subText: 'Minimum 3 questions recommended for a reliable hiring decision',
            reportRecommendation: 'INSUFFICIENT DATA (Minimum 3 questions recommended)',
            executiveSummary: 'Preliminary evaluation in progress. Further technical evaluation recommended before finalizing a hiring decision.'
        };
    }
    if (overallAvg >= 2.5) {
        return {
            verdictText: '✅ HIRE',
            badgeClass: 'hire',
            subText: 'Meets Senior / Technical Lead Engineering Bar',
            reportRecommendation: 'HIRE',
            executiveSummary: 'The candidate demonstrates strong technical competence across assessed domains with solid problem-solving skills and fast root-cause identification. Recommended for Senior / Technical Lead Engineer roles.'
        };
    }
    return {
        verdictText: '❌ REJECT',
        badgeClass: 'reject',
        subText: 'Does not meet required senior technical bar',
        reportRecommendation: 'REJECT',
        executiveSummary: 'The candidate did not meet the required technical bar for this role. Key gaps were observed in debugging runtime failure modes, concurrency guarantees, and system architecture.'
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

    // Highlight card border based on assessment
    const card = document.getElementById('q-' + qId);
    if (card) {
        card.style.borderColor = activeRating >= 3 ? '#4ade80' : activeRating === 2 ? '#fb923c' : '#fca5a5';
    }

    // Mark corresponding quick-jump chip as rated
    const jumpChip = document.getElementById('jump-chip-' + qId);
    if (jumpChip) {
        jumpChip.classList.add('rated');
    }
}

function updateTopicHeaderUI(topicKey) {
    const data = getAllData();
    const topic = data.topics[topicKey] || { ratings: {} };
    const ratings = Object.values(topic.ratings || {}).map(r => r.rating);

    const count = ratings.length;
    const total = TOPIC_REGISTRY[topicKey]?.totalQuestions || 10;

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
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        card.classList.remove('highlight-pulse');
        void card.offsetWidth; // Trigger DOM reflow to restart animation
        card.classList.add('highlight-pulse');
    }
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

function initTopicPage(topicKey) {
    window.currentTopicKey = topicKey;
    const data = getAllData();

    const topic = data.topics[topicKey] || { ratings: {} };
    for (const [qId, item] of Object.entries(topic.ratings || {})) {
        updateQuestionRatingUI(parseInt(qId, 10), item.rating);
    }

    updateTopicHeaderUI(topicKey);
    initBackToTop();
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
    document.querySelectorAll('.question-card').forEach(c => c.style.borderColor = '');
    document.querySelectorAll('.jump-chip').forEach(c => c.classList.remove('rated'));

    updateTopicHeaderUI(topicKey);
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
    const modal = document.getElementById('codeModal');
    if (modal) modal.classList.add('show');
}

function closeCodeSnippetModal() {
    const modal = document.getElementById('codeModal');
    if (modal) modal.classList.remove('show');
}

function copyModalCode() {
    const preEl = document.getElementById('codeModalPre');
    if (!preEl) return;
    navigator.clipboard.writeText(preEl.textContent).then(() => {
        const btn = document.getElementById('copyCodeBtn');
        const orig = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => btn.textContent = orig, 2000);
    });
}

/* ─────────────────────────────────────────────────────
   MASTER SCORECARD (index.html)
───────────────────────────────────────────────────── */
function initIndexPage() {
    renderMasterScorecard();
}

function renderMasterScorecard() {
    const data = getAllData();

    let grandCount = 0;
    const tableBody = document.getElementById('masterSummaryTableBody');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    let allRatings = [];

    for (const [key, meta] of Object.entries(TOPIC_REGISTRY)) {
        const topic   = data.topics[key] || { ratings: {} };
        const ratings = Object.values(topic.ratings || {}).map(r => r.rating);
        const count   = ratings.length;
        grandCount   += count;

        ratings.forEach(r => allRatings.push(r));

        const avg  = count > 0 ? ratings.reduce((a, b) => a + b, 0) / count : null;
        const prof = calcProficiency(avg);

        const countCell = `${count} of ${meta.totalQuestions} questions`;
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
    const rec = calculateRecommendation(overallAvg, grandCount);
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
function openMasterSummaryModal() {
    const data = getAllData();
    let hasData = false;
    let skillBlocks = [];
    let allRatings = [];

    for (const [key, meta] of Object.entries(TOPIC_REGISTRY)) {
        const topic   = data.topics[key] || { ratings: {} };
        const entries = Object.entries(topic.ratings || {});
        if (entries.length === 0) continue;

        hasData = true;
        const ratings = entries.map(([, v]) => v.rating);
        allRatings.push(...ratings);

        const avg  = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        const prof = calcProficiency(avg);

        // Sort by question ID for consistent ordering
        entries.sort((a, b) => parseInt(a[0], 10) - parseInt(b[0], 10));

        // Format technology block with executive explanation (NO NUMBERS)
        let block = `• ${meta.shortTitle} — ${prof.label}\n`;
        block += `  Evaluation: ${prof.evalText}\n`;
        block += `  Assessed Concepts:\n`;

        entries.forEach(([, item]) => {
            const rCfg = RATING_CONFIG.find(r => r.val === item.rating);
            const qual = rCfg ? rCfg.qualitative : 'Assessed';
            block += `  - ${item.concept}: ${qual}\n`;
        });

        skillBlocks.push(block);
    }

    if (!hasData) {
        alert('No questions have been assessed yet. Please rate candidate answers in any section (e.g. Java, Spring) first.');
        return;
    }

    const overallAvg = allRatings.reduce((a, b) => a + b, 0) / allRatings.length;
    const overallProf = calcProficiency(overallAvg);
    const rec = calculateRecommendation(overallAvg, allRatings.length);

    // Build the clean, non-numerical Management/HR report
    let report = `TECHNICAL INTERVIEW ASSESSMENT REPORT\n`;
    report += `=====================================\n`;
    report += `Evaluation Date: ${new Date().toLocaleDateString()}\n`;
    report += `Calculated Recommendation: ${rec.reportRecommendation}\n`;
    report += `Overall Technical Assessment: ${overallProf.label}\n\n`;

    report += `EXECUTIVE SUMMARY\n`;
    report += `─────────────────\n`;
    report += `${rec.executiveSummary}\n\n`;

    report += `TECHNOLOGY & DOMAIN BREAKDOWN\n`;
    report += `─────────────────────────────\n`;
    report += skillBlocks.join('\n') + '\n';

    report += `RECOMMENDATION CRITERIA\n`;
    report += `───────────────────────\n`;
    report += `• HIRE: Recommended when demonstrating Advanced or Expert proficiency across core backend engineering disciplines.\n`;
    report += `• REJECT: Concluded when critical knowledge gaps or intermediate/beginner ratings predominate, failing the senior bar.\n\n`;

    report += `QUALITATIVE PROFICIENCY DEFINITIONS\n`;
    report += `───────────────────────────────────\n`;
    report += `• Expert: Deep mastery of runtime mechanics, low-level architecture, and design trade-offs.\n`;
    report += `• Advanced: Solid practical competence, quick root-cause diagnosis, and clean idiomatic solutions.\n`;
    report += `• Intermediate: Solves standard problems; requires guidance on concurrency or edge cases.\n`;
    report += `• Beginner: Basic syntax awareness; struggles with runtime failure modes and memory models.\n`;

    const ta = document.getElementById('masterSummaryTextarea');
    if (ta) ta.value = report;

    const modal = document.getElementById('masterSummaryModal');
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

function resetAllInterviewData() {
    if (confirm('Reset ALL candidate evaluations across ALL sections?')) {
        localStorage.removeItem(STORAGE_KEY);
        renderMasterScorecard();
    }
}
