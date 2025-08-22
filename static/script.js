// Initialize CodeMirror editor
let editor;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CodeMirror
    const textarea = document.getElementById('codeEditor');
    editor = CodeMirror.fromTextArea(textarea, {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        highlightSelectionMatches: true,
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
    });

    // Set editor size
    editor.setSize("100%", "500px");

    // Get DOM elements
    const runBtn = document.getElementById('runBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const smartRunBtn = document.getElementById('smartRunBtn');
    const clearBtn = document.getElementById('clearBtn');
    const form = document.getElementById('codeForm');

    // Event listeners
    runBtn.addEventListener('click', runCode);
    analyzeBtn.addEventListener('click', analyzeCode);
    smartRunBtn.addEventListener('click', smartRunCode);
    clearBtn.addEventListener('click', clearOutput);

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        runCode();
    });

    // Keyboard shortcuts
    editor.setOption("extraKeys", {
        "Ctrl-Enter": runCode,
        "Cmd-Enter": runCode,
        "Ctrl-Shift-A": analyzeCode,
        "Cmd-Shift-A": analyzeCode
    });
});

async function runCode() {
    const runBtn = document.getElementById('runBtn');
    const output = document.getElementById('output');
    const loading = document.getElementById('loading');

    // Get code from editor
    const code = editor.getValue().trim();
    
    if (!code) {
        showOutput('No code to run!', 'error');
        return;
    }

    // Show loading state
    runBtn.disabled = true;
    runBtn.textContent = '⏳ Running...';
    loading.classList.remove('hidden');
    output.classList.remove('success', 'error');
    output.textContent = '';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('code', code);

        // Send request to backend
        const response = await fetch('/compile', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Hide loading
        loading.classList.add('hidden');

        if (result.success) {
            showOutput(result.output || 'Code executed successfully (no output)', 'success');
        } else {
            showOutput(result.error || 'Unknown error occurred', 'error');
        }

    } catch (error) {
        loading.classList.add('hidden');
        showOutput(`Network error: ${error.message}`, 'error');
    } finally {
        // Reset button
        runBtn.disabled = false;
        runBtn.textContent = '▶️ Run Code';
    }
}

async function analyzeCode() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analysisResults = document.getElementById('analysisResults');
    const analysisLoading = document.getElementById('analysisLoading');
    const analysisStatus = document.getElementById('analysisStatus');

    // Get code from editor
    const code = editor.getValue().trim();
    
    if (!code) {
        showAnalysisResults({
            success: false,
            error: 'No code to analyze!'
        });
        return;
    }

    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '🔍 Analyzing...';
    analysisLoading.classList.remove('hidden');
    analysisResults.innerHTML = '';
    analysisStatus.textContent = '';
    analysisStatus.className = 'analysis-status';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('code', code);

        // Send request to backend
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Hide loading
        analysisLoading.classList.add('hidden');

        // Show analysis results
        showAnalysisResults(result);

    } catch (error) {
        analysisLoading.classList.add('hidden');
        showAnalysisResults({
            success: false,
            error: `Network error: ${error.message}`
        });
    } finally {
        // Reset button
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 Analyze';
    }
}

async function smartRunCode() {
    const smartRunBtn = document.getElementById('smartRunBtn');
    const output = document.getElementById('output');
    const loading = document.getElementById('loading');
    const analysisResults = document.getElementById('analysisResults');
    const analysisLoading = document.getElementById('analysisLoading');

    // Get code from editor
    const code = editor.getValue().trim();
    
    if (!code) {
        showOutput('No code to run!', 'error');
        return;
    }

    // Show loading state for both panels
    smartRunBtn.disabled = true;
    smartRunBtn.textContent = '🧠 Smart Running...';
    loading.classList.remove('hidden');
    analysisLoading.classList.remove('hidden');
    output.classList.remove('success', 'error');
    output.textContent = '';
    analysisResults.innerHTML = '';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('code', code);

        // Send request to backend for analysis and execution
        const response = await fetch('/analyze-and-compile', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Hide loading
        loading.classList.add('hidden');
        analysisLoading.classList.add('hidden');

        // Show analysis results
        if (result.analysis) {
            showAnalysisResults(result.analysis);
        }

        // Show execution results
        if (result.execution) {
            if (result.execution.success) {
                showOutput(result.execution.output || 'Code executed successfully (no output)', 'success');
            } else {
                showOutput(result.execution.error || 'Unknown error occurred', 'error');
            }
        }

    } catch (error) {
        loading.classList.add('hidden');
        analysisLoading.classList.add('hidden');
        showOutput(`Network error: ${error.message}`, 'error');
    } finally {
        // Reset button
        smartRunBtn.disabled = false;
        smartRunBtn.textContent = '🧠 Smart Run';
    }
}

function showAnalysisResults(result) {
    const analysisResults = document.getElementById('analysisResults');
    const analysisStatus = document.getElementById('analysisStatus');
    
    if (!result.success && result.error) {
        analysisResults.innerHTML = `
            <div class="issue-item error">
                <div class="issue-type">Error</div>
                <div class="issue-description">${result.error}</div>
            </div>
        `;
        analysisStatus.textContent = 'Error';
        analysisStatus.className = 'analysis-status danger';
        return;
    }

    let html = '';
    
    // Update status indicator
    if (result.is_safe) {
        const hasWarnings = result.security_issues.some(issue => issue.severity === 'warning') ||
                           result.syntax_errors.length > 0;
        if (hasWarnings) {
            analysisStatus.textContent = 'Safe with warnings';
            analysisStatus.className = 'analysis-status warning';
        } else {
            analysisStatus.textContent = 'Safe';
            analysisStatus.className = 'analysis-status safe';
        }
    } else {
        analysisStatus.textContent = 'Unsafe';
        analysisStatus.className = 'analysis-status danger';
    }

    // Show syntax errors
    if (result.syntax_errors && result.syntax_errors.length > 0) {
        html += '<div class="syntax-errors-section">';
        result.syntax_errors.forEach(error => {
            html += `
                <div class="issue-item error">
                    <div class="issue-type">Syntax Error (Line ${error.line || 'Unknown'})</div>
                    <div class="issue-description">${error.message}</div>
                </div>
            `;
        });
        html += '</div>';
    }

    // Show security issues
    if (result.security_issues && result.security_issues.length > 0) {
        html += '<div class="security-issues-section">';
        result.security_issues.forEach(issue => {
            const severityClass = issue.severity === 'high' ? 'error' : 
                                 issue.severity === 'warning' ? 'warning' : 'info';
            html += `
                <div class="issue-item ${severityClass}">
                    <div class="issue-type">${issue.type} (${issue.severity})</div>
                    <div class="issue-description">${issue.description}</div>
                    ${issue.pattern ? `<div class="issue-pattern">Pattern: <code>${issue.pattern}</code></div>` : ''}
                </div>
            `;
        });
        html += '</div>';
    }

    // Show suggestions
    if (result.suggestions && result.suggestions.length > 0) {
        html += `
            <div class="suggestions-section">
                <div class="suggestions-title">💡 Suggestions</div>
        `;
        result.suggestions.forEach(suggestion => {
            html += `<div class="suggestion-item">${suggestion}</div>`;
        });
        html += '</div>';
    }

    // Show fixed code if available
    if (result.fixed_code && result.fixed_code.trim()) {
        html += `
            <div class="fixed-code-section">
                <div class="fixed-code-title">🔧 Improved Code</div>
                <div class="fixed-code">${escapeHtml(result.fixed_code)}</div>
            </div>
        `;
    }

    // Show explanation if available
    if (result.explanation) {
        html += `
            <div class="explanation-section">
                <div class="suggestions-title">📝 Analysis Explanation</div>
                <div class="suggestion-item">${result.explanation}</div>
            </div>
        `;
    }

    if (!html) {
        html = '<div class="analysis-placeholder">✅ No issues found! Your code looks good.</div>';
    }

    analysisResults.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showOutput(text, type) {
    const output = document.getElementById('output');
    output.textContent = text;
    output.classList.remove('success', 'error');
    
    if (type === 'success') {
        output.classList.add('success');
    } else if (type === 'error') {
        output.classList.add('error');
    }
}

function clearOutput() {
    const output = document.getElementById('output');
    output.textContent = 'Ready to run your Python code!';
    output.classList.remove('success', 'error');
}

// Add example buttons (you can extend this)
function loadExample(exampleName) {
    if (examples[exampleName]) {
        editor.setValue(examples[exampleName]);
    }
}
