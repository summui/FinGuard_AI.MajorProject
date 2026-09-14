// Contract document upload, clause extraction, and risk report rendering
// Contract analyzer UI logic — Sam (Track B)

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const resultSection = document.getElementById('result-section');
const errorBox = document.getElementById('error-box');

// drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) processFile(file);
}

async function processFile(file) {
    // client-side validation
    if (!file.name.endsWith('.pdf')) {
        showError('Only PDF files are accepted.');
        return;
    }
    if (file.size > 15 * 1024 * 1024) {
        showError('File exceeds 15MB limit.');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('file', file);

        const token = localStorage.getItem('token');
        const response = await fetch('/contracts/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Analysis failed.');
        }

        const result = await response.json();
        showResult(result, file.name);
        loadHistory();

    } catch (err) {
        showError(err.message);
    }
}

function showLoading() {
    dropZone.style.display = 'none';
    errorBox.style.display = 'none';
    loadingSection.style.display = 'block';
    resultSection.style.display = 'none';
}

function showResult(data, filename) {
    loadingSection.style.display = 'none';
    resultSection.style.display = 'block';

    // filename
    document.getElementById('result-filename').textContent = filename;

    // risk badge
    const badge = document.getElementById('risk-badge');
    badge.textContent = data.risk_level + ' Risk';
    badge.className = 'risk-badge';
    if (data.risk_level === 'High') badge.classList.add('risk-high');
    else if (data.risk_level === 'Medium') badge.classList.add('risk-medium');
    else badge.classList.add('risk-low');

    // summary
    document.getElementById('result-summary').textContent = data.summary;

    // red flags
    const redList = document.getElementById('red-flags-list');
    const redFlags = data.risks.filter(r => r.flag_type === 'red');
    if (redFlags.length === 0) {
        redList.innerHTML = '<p style="font-size:13px;color:#999">No red flags found.</p>';
    } else {
        redList.innerHTML = redFlags.map(f => `
      <div class="flag-item flag-red">
        <span class="flag-icon">🔴</span>
        <div class="flag-text">
          <div class="flag-category">${f.category}</div>
          ${f.clause_text}
        </div>
      </div>
    `).join('');
    }

    // green flags
    const greenList = document.getElementById('green-flags-list');
    const greenFlags = data.risks.filter(r => r.flag_type === 'green');
    if (greenFlags.length === 0) {
        greenList.innerHTML = '<p style="font-size:13px;color:#999">No green flags found.</p>';
    } else {
        greenList.innerHTML = greenFlags.map(f => `
      <div class="flag-item flag-green">
        <span class="flag-icon">🟢</span>
        <div class="flag-text">
          <div class="flag-category">${f.category}</div>
          ${f.clause_text}
        </div>
      </div>
    `).join('');
    }
}

function showError(message) {
    loadingSection.style.display = 'none';
    errorBox.style.display = 'block';
    document.getElementById('error-message').textContent = message;
}

function resetUpload() {
    dropZone.style.display = 'block';
    errorBox.style.display = 'none';
    loadingSection.style.display = 'none';
    resultSection.style.display = 'none';
    fileInput.value = '';
}

async function loadHistory() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/contracts', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const contracts = await response.json();
        const list = document.getElementById('history-list');

        if (contracts.length === 0) {
            list.innerHTML = '<p style="font-size:13px;color:#999">No contracts analyzed yet.</p>';
            return;
        }

        list.innerHTML = contracts.map(c => `
      <div class="history-row">
        <div>
          <div class="history-name">📄 ${c.filename}</div>
          <div class="history-date">Risk score: ${c.risk_score}/100</div>
        </div>
        <span class="risk-badge ${c.risk_level === 'High' ? 'risk-high' :
                c.risk_level === 'Medium' ? 'risk-medium' : 'risk-low'
            }">${c.risk_level}</span>
      </div>
    `).join('');
    } catch (e) {
        console.log('History load failed', e);
    }
}

// load history on page open
loadHistory();