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
    const clearBtn = document.getElementById('clearBtn');
    const form = document.getElementById('codeForm');

    // Run code event
    runBtn.addEventListener('click', runCode);
    
    // Clear output event
    clearBtn.addEventListener('click', clearOutput);

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        runCode();
    });

    // Keyboard shortcut (Ctrl+Enter or Cmd+Enter)
    editor.setOption("extraKeys", {
        "Ctrl-Enter": runCode,
        "Cmd-Enter": runCode
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
