// DOM elements
const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const formatSelect = document.getElementById('formatSelect');
const historyList = document.getElementById('historyList');
const statsLabel = document.getElementById('statsLabel');
const notification = document.getElementById('notification');
const notificationText = document.getElementById('notificationText');

let currentHistory = [];
let convertTimeout = null;

// Auto-convert on input
inputText.addEventListener('input', () => {
  clearTimeout(convertTimeout);
  convertTimeout = setTimeout(convertText, 500);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl+Enter = Convert
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault();
    convertText();
  }
  // Ctrl+Shift+C = Copy
  if (e.ctrlKey && e.shiftKey && e.key === 'C') {
    e.preventDefault();
    copyOutput();
  }
  // Escape = Clear
  if (e.key === 'Escape') {
    inputText.value = '';
    outputText.innerHTML = '<span class="placeholder">Your Markdown will appear here...</span>';
  }
});

// Convert text
async function convertText() {
  const text = inputText.value.trim();
  if (!text) return;

  const options = {
    format: formatSelect.value,
    stats: true,
  };

  const result = await window.api.convert(text, options);

  if (result.success) {
    const markdown = extractMarkdown(result.markdown);
    outputText.innerHTML = markdown || '<span class="placeholder">Conversion failed</span>';
    
    // Save to history
    await window.api.saveToHistory({
      input: text,
      output: markdown,
    });
    
    loadHistory();
    updateStats(text.length, markdown.length);
  } else {
    showNotification('Conversion failed', true);
  }
}

// Extract markdown from Python output (removes Rich formatting)
function extractMarkdown(raw) {
  const lines = raw.split('\n');
  const markdownLines = [];
  let started = false;

  for (const line of lines) {
    if (line.includes('Markdown Output')) {
      started = true;
      continue;
    }
    if (started && line.trim()) {
      markdownLines.push(line);
    }
  }

  return markdownLines.join('\n') || raw;
}

// Copy to clipboard
async function copyOutput() {
  const text = outputText.innerText || outputText.textContent;
  if (!text || text.includes('will appear here')) return;

  await window.api.copyToClipboard(text);
  showNotification('Copied to clipboard!');
}

// Show notification
function showNotification(message, isError = false) {
  notificationText.textContent = message;
  notification.style.background = isError ? 'var(--danger)' : 'var(--success)';
  notification.classList.remove('hidden');

  setTimeout(() => {
    notification.classList.add('hidden');
  }, 2000);
}

// Update stats
function updateStats(inputLength, outputLength) {
  if (inputLength && outputLength) {
    const saved = inputLength - outputLength;
    const percent = ((saved / inputLength) * 100).toFixed(0);
    statsLabel.textContent = `${percent}% smaller`;
  } else {
    statsLabel.textContent = '';
  }
}

// Insert formatting
function insertFormat(type) {
  const textarea = inputText;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const text = textarea.value;
  const selected = text.substring(start, end);

  let replacement = '';

  switch (type) {
    case 'h1': replacement = `# ${selected || 'Heading 1'}`; break;
    case 'h2': replacement = `## ${selected || 'Heading 2'}`; break;
    case 'h3': replacement = `### ${selected || 'Heading 3'}`; break;
    case 'bold': replacement = `**${selected || 'bold'}**`; break;
    case 'italic': replacement = `*${selected || 'italic'}*`; break;
    case 'code': replacement = `\`${selected || 'code'}\``; break;
    case 'ul': replacement = `- ${selected || 'item'}`; break;
    case 'ol': replacement = `1. ${selected || 'item'}`; break;
    case 'task': replacement = `- [ ] ${selected || 'task'}`; break;
    case 'quote': replacement = `> ${selected || 'quote'}`; break;
    default: break;
  }

  textarea.value = text.substring(0, start) + replacement + text.substring(end);
  textarea.focus();
  textarea.setSelectionRange(start + replacement.length, start + replacement.length);
}

// Load history
async function loadHistory() {
  currentHistory = await window.api.getHistory();
  renderHistory();
}

// Render history
function renderHistory() {
  if (currentHistory.length === 0) {
    historyList.innerHTML = '<p class="empty-state">No history yet</p>';
    return;
  }

  historyList.innerHTML = currentHistory.map(item => `
    <div class="history-item" onclick="loadFromHistory(${item.id})">
      <div class="history-item-title">${escapeHtml(item.title || 'Untitled')}</div>
      <div class="history-item-meta">
        ${formatDate(item.timestamp)} · ${item.input.length} → ${item.output.length} chars
      </div>
    </div>
  `).join('');
}

// Load from history
function loadFromHistory(id) {
  const item = currentHistory.find(h => h.id === id);
  if (item) {
    inputText.value = item.input;
    outputText.innerHTML = item.output;
  }
}

// Clear history
async function clearHistory() {
  await window.api.clearHistory();
  currentHistory = [];
  renderHistory();
  showNotification('History cleared');
}

// Escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Format date
function formatDate(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;

  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return date.toLocaleDateString();
}

// Listen for focus event from main process
window.api.onFocusInput(() => {
  inputText.focus();
});

// Load history on start
loadHistory();