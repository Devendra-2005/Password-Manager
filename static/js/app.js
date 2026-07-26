// SecureVault Web Application State
let appState = {
  hasMasterPassword: false,
  authenticated: false,
  currentCategory: 'All',
  searchQuery: '',
  credentials: [],
  editingId: null,
  isGeneratorFromForm: false
};

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const icon = type === 'success' ? '✓' : '⚠️';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// App Initialization & Status Check
async function initApp() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    
    if (data.success) {
      appState.hasMasterPassword = data.has_master_password;
      appState.authenticated = data.authenticated;

      if (!appState.hasMasterPassword) {
        showSetupScreen();
      } else if (!appState.authenticated) {
        showLoginScreen();
      } else {
        showDashboardScreen();
      }
    }
  } catch (err) {
    console.error('Error initializing app:', err);
    showToast('Server connection failed', 'danger');
  }
}

// View Switches
function showSetupScreen() {
  document.getElementById('auth-container').classList.remove('hidden');
  document.getElementById('app-container').classList.add('hidden');
  
  document.getElementById('auth-subtitle').innerText = 'Create a Master Password to secure your vault.';
  document.getElementById('strength-box').classList.remove('hidden');
  document.getElementById('confirm-pwd-group').classList.remove('hidden');
  document.getElementById('auth-submit-btn').innerHTML = '<span>🔒 Set Master Password & Unlock</span>';
}

function showLoginScreen() {
  document.getElementById('auth-container').classList.remove('hidden');
  document.getElementById('app-container').classList.add('hidden');

  document.getElementById('auth-subtitle').innerText = 'Enter your Master Password to access your credentials.';
  document.getElementById('strength-box').classList.add('hidden');
  document.getElementById('confirm-pwd-group').classList.add('hidden');
  document.getElementById('auth-submit-btn').innerHTML = '<span>🔓 Unlock Vault</span>';
}

function showDashboardScreen() {
  document.getElementById('auth-container').classList.add('hidden');
  document.getElementById('app-container').classList.remove('hidden');

  loadCredentials();
}

// Password Strength Bar
async function handlePasswordInput() {
  if (appState.hasMasterPassword) return; // Only show on setup screen

  const pwd = document.getElementById('master-password').value;
  const barFill = document.getElementById('strength-bar-fill');
  const label = document.getElementById('strength-label');

  if (!pwd) {
    barFill.style.width = '0%';
    label.innerText = 'Strength: Empty';
    return;
  }

  try {
    const res = await fetch('/api/eval-strength', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pwd })
    });
    const data = await res.json();

    if (data.success) {
      barFill.style.width = `${data.score}%`;
      barFill.style.backgroundColor = data.color;
      label.innerText = `Strength: ${data.label}`;
      label.style.color = data.color;
    }
  } catch (e) {
    console.error('Strength eval error:', e);
  }
}

function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    btn.innerText = '🙈';
  } else {
    input.type = 'password';
    btn.innerText = '👁️';
  }
}

// Auth Submit
async function handleAuthSubmit(event) {
  event.preventDefault();
  const errDiv = document.getElementById('auth-error');
  errDiv.classList.add('hidden');

  const password = document.getElementById('master-password').value.trim();

  if (!appState.hasMasterPassword) {
    const confirm = document.getElementById('confirm-password').value.trim();
    if (password !== confirm) {
      errDiv.innerText = 'Passwords do not match!';
      errDiv.classList.remove('hidden');
      return;
    }

    try {
      const res = await fetch('/api/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      const data = await res.json();

      if (data.success) {
        showToast('Vault created successfully!', 'success');
        appState.hasMasterPassword = true;
        appState.authenticated = true;
        showDashboardScreen();
      } else {
        errDiv.innerText = data.error || 'Failed to setup Master Password';
        errDiv.classList.remove('hidden');
      }
    } catch (e) {
      errDiv.innerText = 'Connection error. Please try again.';
      errDiv.classList.remove('hidden');
    }
  } else {
    // Login Mode
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });
      const data = await res.json();

      if (data.success) {
        showToast('Vault unlocked!', 'success');
        appState.authenticated = true;
        showDashboardScreen();
      } else {
        errDiv.innerText = data.error || 'Incorrect Master Password!';
        errDiv.classList.remove('hidden');
      }
    } catch (e) {
      errDiv.innerText = 'Server error during login.';
      errDiv.classList.remove('hidden');
    }
  }
}

async function handleLogout() {
  if (confirm('Are you sure you want to lock your vault and logout?')) {
    await fetch('/api/logout', { method: 'POST' });
    appState.authenticated = false;
    document.getElementById('master-password').value = '';
    showLoginScreen();
    showToast('Vault locked', 'success');
  }
}

// Credentials Loader & Search
async function loadCredentials() {
  const query = encodeURIComponent(appState.searchQuery);
  const category = encodeURIComponent(appState.currentCategory);

  try {
    const res = await fetch(`/api/credentials?query=${query}&category=${category}`);
    const data = await res.json();

    if (data.success) {
      appState.credentials = data.data;
      renderTable(data.data);
      updateStats(data.data);
    }
  } catch (err) {
    console.error('Error fetching credentials:', err);
  }
}

function updateStats(credentials) {
  document.getElementById('stat-total').innerText = credentials.length;

  const categories = new Set(credentials.map(c => c.category));
  document.getElementById('stat-categories').innerText = categories.size;
}

function renderTable(credentials) {
  const tbody = document.getElementById('credentials-tbody');
  const emptyState = document.getElementById('empty-state');

  tbody.innerHTML = '';

  if (!credentials || credentials.length === 0) {
    emptyState.classList.remove('hidden');
    return;
  } else {
    emptyState.classList.add('hidden');
  }

  credentials.forEach(cred => {
    const tr = document.createElement('tr');
    const catClass = `badge-${cred.category.toLowerCase()}`;

    tr.innerHTML = `
      <td>
        <strong style="color: #FFFFFF;">${escapeHtml(cred.website)}</strong>
        ${cred.notes ? `<br><small style="color: var(--text-muted);">${escapeHtml(cred.notes)}</small>` : ''}
      </td>
      <td>${escapeHtml(cred.username)}</td>
      <td><span class="badge ${catClass}">${cred.category}</span></td>
      <td>
        <span id="pwd-display-${cred.id}" class="pwd-masked">••••••••••••</span>
      </td>
      <td>
        <div class="table-actions">
          <button class="btn btn-sm btn-secondary" title="Show Password" onclick="toggleTablePassword(${cred.id}, '${escapeHtml(cred.password)}', this)">👁️</button>
          <button class="btn btn-sm btn-secondary" title="Copy Password" onclick="copyToClipboard('${escapeHtml(cred.password)}', '${escapeHtml(cred.website)}')">📋</button>
          <button class="btn btn-sm btn-secondary" title="Edit" onclick="openEditModal(${cred.id})">✏️</button>
          <button class="btn btn-sm btn-danger-outline" title="Delete" onclick="deleteCredential(${cred.id}, '${escapeHtml(cred.website)}')">🗑️</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function toggleTablePassword(id, plainPassword, btn) {
  const elem = document.getElementById(`pwd-display-${id}`);
  if (elem.classList.contains('pwd-masked')) {
    elem.innerText = plainPassword;
    elem.classList.remove('pwd-masked');
    btn.innerText = '🙈';
  } else {
    elem.innerText = '••••••••••••';
    elem.classList.add('pwd-masked');
    btn.innerText = '👁️';
  }
}

function copyToClipboard(text, website) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(`Password for '${website}' copied to clipboard!`, 'success');
    }).catch(() => {
      fallbackCopy(text, website);
    });
  } else {
    fallbackCopy(text, website);
  }
}

function fallbackCopy(text, website) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand('copy');
  document.body.removeChild(textArea);
  showToast(`Password for '${website}' copied!`, 'success');
}

function handleSearchInput() {
  appState.searchQuery = document.getElementById('search-input').value.trim();
  loadCredentials();
}

function clearSearch() {
  document.getElementById('search-input').value = '';
  appState.searchQuery = '';
  loadCredentials();
}

function selectCategory(category, btn) {
  appState.currentCategory = category;
  document.querySelectorAll('#category-pills .pill').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  loadCredentials();
}

// Modal Handlers
function openAddModal() {
  appState.editingId = null;
  document.getElementById('modal-title').innerText = '➕ Add New Credential';
  document.getElementById('credential-form').reset();
  document.getElementById('cred-id').value = '';
  document.getElementById('modal-error').classList.add('hidden');
  document.getElementById('credential-modal').classList.remove('hidden');
}

function openEditModal(id) {
  const cred = appState.credentials.find(c => c.id === id);
  if (!cred) return;

  appState.editingId = id;
  document.getElementById('modal-title').innerText = '✏️ Edit Credential';
  document.getElementById('cred-id').value = id;
  document.getElementById('cred-website').value = cred.website;
  document.getElementById('cred-username').value = cred.username;
  document.getElementById('cred-password').value = cred.password;
  document.getElementById('cred-category').value = cred.category;
  document.getElementById('cred-notes').value = cred.notes || '';
  document.getElementById('modal-error').classList.add('hidden');
  document.getElementById('credential-modal').classList.remove('hidden');
}

function closeCredentialModal() {
  document.getElementById('credential-modal').classList.add('hidden');
}

async function saveCredential(event) {
  event.preventDefault();
  const errDiv = document.getElementById('modal-error');
  errDiv.classList.add('hidden');

  const payload = {
    website: document.getElementById('cred-website').value.trim(),
    username: document.getElementById('cred-username').value.trim(),
    password: document.getElementById('cred-password').value.trim(),
    category: document.getElementById('cred-category').value,
    notes: document.getElementById('cred-notes').value.trim()
  };

  const isEdit = !!appState.editingId;
  const url = isEdit ? `/api/credentials/${appState.editingId}` : '/api/credentials';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      showToast(isEdit ? 'Credential updated!' : 'Credential saved!', 'success');
      closeCredentialModal();
      loadCredentials();
    } else {
      errDiv.innerText = data.error || 'Failed to save credential.';
      errDiv.classList.remove('hidden');
    }
  } catch (e) {
    errDiv.innerText = 'Network error saving credential.';
    errDiv.classList.remove('hidden');
  }
}

async function deleteCredential(id, website) {
  if (confirm(`Are you sure you want to delete credential for '${website}'?`)) {
    try {
      const res = await fetch(`/api/credentials/${id}`, { method: 'DELETE' });
      const data = await res.json();

      if (data.success) {
        showToast(`Deleted '${website}'`, 'success');
        loadCredentials();
      } else {
        showToast(data.error || 'Could not delete credential', 'danger');
      }
    } catch (e) {
      showToast('Error deleting credential', 'danger');
    }
  }
}

// Password Generator Modal
function openGeneratorModal() {
  appState.isGeneratorFromForm = false;
  document.getElementById('btn-use-generated').classList.add('hidden');
  document.getElementById('generator-modal').classList.remove('hidden');
  generateNewPassword();
}

function fillWithGenerator() {
  appState.isGeneratorFromForm = true;
  document.getElementById('btn-use-generated').classList.remove('hidden');
  document.getElementById('generator-modal').classList.remove('hidden');
  generateNewPassword();
}

function closeGeneratorModal() {
  document.getElementById('generator-modal').classList.add('hidden');
}

function updateGenLength(val) {
  document.getElementById('gen-length-val').innerText = val;
  generateNewPassword();
}

async function generateNewPassword() {
  const length = parseInt(document.getElementById('gen-length').value);
  const use_upper = document.getElementById('gen-upper').checked;
  const use_lower = document.getElementById('gen-lower').checked;
  const use_digits = document.getElementById('gen-digits').checked;
  const use_symbols = document.getElementById('gen-symbols').checked;

  try {
    const res = await fetch('/api/generate-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ length, use_upper, use_lower, use_digits, use_symbols })
    });
    const data = await res.json();

    if (data.success) {
      document.getElementById('gen-output').value = data.password;
    }
  } catch (e) {
    console.error('Password generation failed:', e);
  }
}

function copyGeneratedPassword() {
  const pwd = document.getElementById('gen-output').value;
  if (pwd) {
    copyToClipboard(pwd, 'Generator');
  }
}

function useGeneratedPasswordInForm() {
  const pwd = document.getElementById('gen-output').value;
  if (pwd) {
    document.getElementById('cred-password').value = pwd;
    closeGeneratorModal();
    showToast('Password applied to form!', 'success');
  }
}
