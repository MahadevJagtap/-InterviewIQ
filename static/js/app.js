/**
 * InterviewIQ — Frontend Application Logic
 * Handles file upload, API calls, DOM rendering, filtering, and PDF export.
 */

// ─── DOM References ──────────────────────────────────────────────────────────
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const fileRemove = document.getElementById('file-remove');
const btnGenerate = document.getElementById('btn-generate');
const numQuestions = document.getElementById('num-questions');
const numQuestionsValue = document.getElementById('num-questions-value');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const uploadSection = document.getElementById('upload-section');
const configSection = document.getElementById('config-section');
const analysisContent = document.getElementById('analysis-content');
const questionsList = document.getElementById('questions-list');
const resultsCount = document.getElementById('results-count');
const filterBar = document.getElementById('filter-bar');
const errorToast = document.getElementById('error-toast');
const errorMessage = document.getElementById('error-message');
const errorDismiss = document.getElementById('error-dismiss');
const btnExportPdf = document.getElementById('btn-export-pdf');

let selectedFile = null;
let generatedData = null;

// ─── File Upload ─────────────────────────────────────────────────────────────
dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

fileRemove.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    dropzone.style.display = 'block';
    btnGenerate.disabled = true;
});

function handleFile(file) {
    const ext = file.name.toLowerCase().split('.').pop();
    if (!['pdf', 'docx'].includes(ext)) {
        showError('Please upload a PDF or DOCX file.');
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        showError('File is too large. Maximum size is 10MB.');
        return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);
    fileInfo.style.display = 'block';
    dropzone.style.display = 'none';
    btnGenerate.disabled = false;
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ─── Slider ──────────────────────────────────────────────────────────────────
numQuestions.addEventListener('input', () => {
    numQuestionsValue.textContent = numQuestions.value;
});

// ─── Toggle Buttons ──────────────────────────────────────────────────────────
document.getElementById('difficulty-group').addEventListener('click', (e) => {
    if (e.target.classList.contains('toggle-btn')) {
        document.querySelectorAll('#difficulty-group .toggle-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
    }
});

// ─── Generate Questions ──────────────────────────────────────────────────────
btnGenerate.addEventListener('click', generateQuestions);

async function generateQuestions() {
    if (!selectedFile) return;

    // Gather config
    const difficulty = document.querySelector('#difficulty-group .toggle-btn.active').dataset.value;
    const numQ = parseInt(numQuestions.value);
    const categories = Array.from(document.querySelectorAll('#category-group input:checked'))
        .map(cb => cb.value)
        .join(',');

    if (!categories) {
        showError('Please select at least one question category.');
        return;
    }

    // Build form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('difficulty', difficulty);
    formData.append('num_questions', numQ);
    formData.append('categories', categories);

    // Show loading
    uploadSection.style.display = 'none';
    configSection.style.display = 'none';
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'block';
    animateLoading();

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Generation failed.');
        }

        generatedData = await response.json();
        renderResults(generatedData);

    } catch (err) {
        showError(err.message);
        // Show upload again
        uploadSection.style.display = 'block';
        configSection.style.display = 'block';
    } finally {
        loadingSection.style.display = 'none';
    }
}

// ─── Loading Animation ──────────────────────────────────────────────────────
function animateLoading() {
    const steps = ['step-1', 'step-2', 'step-3'];
    const texts = ['Parsing your document...', 'Analyzing job description...', 'Generating interview questions...'];
    const loaderText = document.getElementById('loader-text');
    let current = 0;

    function advance() {
        if (current > 0) {
            document.getElementById(steps[current - 1]).classList.remove('active');
            document.getElementById(steps[current - 1]).classList.add('done');
        }
        if (current < steps.length) {
            document.getElementById(steps[current]).classList.add('active');
            loaderText.textContent = texts[current];
            current++;
        }
    }

    advance();
    setTimeout(advance, 2000);
    setTimeout(advance, 5000);
}

// ─── Render Results ──────────────────────────────────────────────────────────
function renderResults(data) {
    renderAnalysis(data.jd_analysis);
    renderQuestions(data.questions);
    buildFilterBar(data.questions);
    resultsCount.textContent = data.total_questions;
    resultsSection.style.display = 'block';

    // Show reset option
    uploadSection.style.display = 'block';
    configSection.style.display = 'block';

    // Scroll to results
    document.getElementById('analysis-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderAnalysis(analysis) {
    const skillCategoryClass = (cat) => {
        const lower = cat.toLowerCase();
        if (lower.includes('soft')) return 'soft';
        if (lower.includes('tool')) return 'tool';
        if (lower.includes('domain')) return 'domain';
        return '';
    };

    const skillsHtml = analysis.key_skills.map(s =>
        `<span class="skill-tag ${skillCategoryClass(s.category)}" title="${s.proficiency} — ${s.category}">${s.name}</span>`
    ).join('');

    analysisContent.innerHTML = `
        <div class="analysis-item">
            <div class="analysis-label">Role Title</div>
            <div class="analysis-value">${esc(analysis.role_title)}</div>
        </div>
        <div class="analysis-item">
            <div class="analysis-label">Seniority Level</div>
            <div class="analysis-value">${esc(analysis.seniority_level)}</div>
        </div>
        ${analysis.company_name ? `
        <div class="analysis-item">
            <div class="analysis-label">Company</div>
            <div class="analysis-value">${esc(analysis.company_name)}</div>
        </div>` : ''}
        <div class="analysis-item">
            <div class="analysis-label">Experience Required</div>
            <div class="analysis-value">${esc(analysis.experience_range)}</div>
        </div>
        ${analysis.education ? `
        <div class="analysis-item">
            <div class="analysis-label">Education</div>
            <div class="analysis-value">${esc(analysis.education)}</div>
        </div>` : ''}
        ${analysis.industry ? `
        <div class="analysis-item">
            <div class="analysis-label">Industry</div>
            <div class="analysis-value">${esc(analysis.industry)}</div>
        </div>` : ''}
        <div class="analysis-item full-width">
            <div class="analysis-label">Role Summary</div>
            <div class="analysis-value">${esc(analysis.role_summary)}</div>
        </div>
        <div class="analysis-item full-width">
            <div class="analysis-label">Key Skills (${analysis.key_skills.length})</div>
            <div class="skills-tags">${skillsHtml}</div>
        </div>
    `;
}

function renderQuestions(questions) {
    questionsList.innerHTML = questions.map((q, i) => `
        <div class="question-card" data-category="${q.category}" style="animation-delay: ${i * 0.06}s">
            <div class="question-header" onclick="toggleQuestion(this)">
                <div class="question-number">${q.id}</div>
                <div class="question-main">
                    <div class="question-text">${esc(q.question)}</div>
                    <div class="question-meta">
                        <span class="question-badge badge-category">${q.category}</span>
                        <span class="question-badge badge-difficulty-${q.difficulty}">${q.difficulty}</span>
                    </div>
                </div>
                <div class="question-toggle">▼</div>
            </div>
            <div class="question-details">
                <div class="question-details-inner">
                    <div class="detail-section">
                        <div class="detail-title">Why Ask This</div>
                        <div class="detail-content">${esc(q.why_ask)}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">Expected Answer</div>
                        <div class="detail-content">${esc(q.expected_answer)}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-title">Evaluation Criteria</div>
                        <div class="rubric-grid">
                            <div class="rubric-item rubric-excellent">
                                <div class="rubric-label">✦ Excellent</div>
                                <div class="rubric-text">${esc(q.evaluation_criteria.excellent)}</div>
                            </div>
                            <div class="rubric-item rubric-acceptable">
                                <div class="rubric-label">● Acceptable</div>
                                <div class="rubric-text">${esc(q.evaluation_criteria.acceptable)}</div>
                            </div>
                            <div class="rubric-item rubric-poor">
                                <div class="rubric-label">▲ Poor / Red Flag</div>
                                <div class="rubric-text">${esc(q.evaluation_criteria.poor)}</div>
                            </div>
                        </div>
                    </div>
                    ${q.follow_up_questions && q.follow_up_questions.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-title">Follow-Up Questions</div>
                        <ul class="followup-list">
                            ${q.follow_up_questions.map(f => `<li>${esc(f)}</li>`).join('')}
                        </ul>
                    </div>` : ''}
                    ${q.relevant_skills && q.relevant_skills.length > 0 ? `
                    <div class="detail-section">
                        <div class="detail-title">Skills Tested</div>
                        <div class="relevant-skills-tags">
                            ${q.relevant_skills.map(s => `<span class="relevant-skill">${esc(s)}</span>`).join('')}
                        </div>
                    </div>` : ''}
                </div>
            </div>
        </div>
    `).join('');
}

// ─── Toggle Question Expand ──────────────────────────────────────────────────
function toggleQuestion(header) {
    const card = header.closest('.question-card');
    card.classList.toggle('expanded');
}

// ─── Filter Bar ──────────────────────────────────────────────────────────────
function buildFilterBar(questions) {
    const categories = [...new Set(questions.map(q => q.category))];
    filterBar.innerHTML = `<button class="filter-btn active" data-filter="all">All</button>` +
        categories.map(c => `<button class="filter-btn" data-filter="${c}">${c}</button>`).join('');

    filterBar.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-btn')) {
            filterBar.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const filter = e.target.dataset.filter;
            document.querySelectorAll('.question-card').forEach(card => {
                if (filter === 'all' || card.dataset.category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    });
}

// ─── PDF Export (Client-side) ────────────────────────────────────────────────
btnExportPdf.addEventListener('click', exportPdf);

function exportPdf() {
    if (!generatedData) return;

    const { jd_analysis, questions } = generatedData;
    let content = [];

    content.push(`INTERVIEW QUESTIONS — ${jd_analysis.role_title.toUpperCase()}`);
    content.push(`${'═'.repeat(60)}`);
    content.push(`Company: ${jd_analysis.company_name || 'N/A'}`);
    content.push(`Seniority: ${jd_analysis.seniority_level}`);
    content.push(`Experience: ${jd_analysis.experience_range}`);
    content.push(`Generated: ${new Date().toLocaleDateString()}`);
    content.push('');
    content.push(`SUMMARY: ${jd_analysis.role_summary}`);
    content.push('');
    content.push(`KEY SKILLS: ${jd_analysis.key_skills.map(s => s.name).join(', ')}`);
    content.push(`${'─'.repeat(60)}`);
    content.push('');

    questions.forEach((q, i) => {
        content.push(`Q${q.id}. [${q.category}] [${q.difficulty}]`);
        content.push(q.question);
        content.push('');
        content.push(`   Why Ask: ${q.why_ask}`);
        content.push('');
        content.push(`   Expected Answer:`);
        content.push(`   ${q.expected_answer}`);
        content.push('');
        content.push(`   Evaluation Criteria:`);
        content.push(`   ✦ Excellent: ${q.evaluation_criteria.excellent}`);
        content.push(`   ● Acceptable: ${q.evaluation_criteria.acceptable}`);
        content.push(`   ▲ Poor: ${q.evaluation_criteria.poor}`);
        content.push('');
        if (q.follow_up_questions && q.follow_up_questions.length > 0) {
            content.push(`   Follow-Up Questions:`);
            q.follow_up_questions.forEach(f => content.push(`   → ${f}`));
            content.push('');
        }
        if (q.relevant_skills && q.relevant_skills.length > 0) {
            content.push(`   Skills Tested: ${q.relevant_skills.join(', ')}`);
        }
        content.push(`${'─'.repeat(60)}`);
        content.push('');
    });

    // Download as text file (reliable cross-browser)
    const blob = new Blob([content.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview_questions_${jd_analysis.role_title.replace(/\s+/g, '_').toLowerCase()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ─── Error Handling ──────────────────────────────────────────────────────────
function showError(msg) {
    errorMessage.textContent = msg;
    errorToast.style.display = 'flex';
    setTimeout(() => {
        errorToast.style.display = 'none';
    }, 8000);
}

errorDismiss.addEventListener('click', () => {
    errorToast.style.display = 'none';
});

// ─── Utilities ───────────────────────────────────────────────────────────────
function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
