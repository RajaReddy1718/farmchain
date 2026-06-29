const apiKeyInput = document.getElementById('apiKey');
const loginUsernameInput = document.getElementById('loginUsername');
const loginPasswordInput = document.getElementById('loginPassword');
const loginStatus = document.getElementById('loginStatus');
const responseOutput = document.getElementById('responseOutput');
const verifyResult = document.getElementById('verifyResult');

function getHeaders(needsAuth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (needsAuth) {
    const apiKey = apiKeyInput.value.trim() || localStorage.getItem('farmchain_api_key');
    if (!apiKey) throw new Error('API key is required for this action.');
    headers['X-API-KEY'] = apiKey;
  }
  return headers;
}

function setApiKey(key) {
  apiKeyInput.value = key;
  if (key) {
    localStorage.setItem('farmchain_api_key', key);
    loginStatus.textContent = 'Logged in';
  } else {
    localStorage.removeItem('farmchain_api_key');
    loginStatus.textContent = 'Not logged in';
  }
}

function loadSavedKey() {
  const saved = localStorage.getItem('farmchain_api_key');
  if (saved) {
    apiKeyInput.value = saved;
    loginStatus.textContent = 'Logged in';
  }
}

async function login() {
  const body = {
    username: loginUsernameInput.value.trim(),
    password: loginPasswordInput.value.trim()
  };
  const result = await doRequest('/auth/login', {
    method: 'POST',
    headers: getHeaders(false),
    body: JSON.stringify(body)
  });
  if (result && result.api_key) {
    setApiKey(result.api_key);
  }
}

async function doRequest(url, options) {
  responseOutput.textContent = 'Loading...';
  const response = await fetch(url, options);
  const text = await response.text();
  try {
    const json = JSON.parse(text);
    responseOutput.textContent = JSON.stringify(json, null, 2);
    return json;
  } catch {
    responseOutput.textContent = text;
    return text;
  }
}

async function registerFarmer() {
  const body = {
    wallet_address: document.getElementById('farmerWallet').value.trim(),
    name: document.getElementById('farmerName').value.trim(),
    farm_name: document.getElementById('farmName').value.trim(),
    location: document.getElementById('farmerLocation').value.trim(),
    certification: document.getElementById('farmerCertification').value.trim()
  };
  const result = await doRequest('/farmer/register', {
    method: 'POST',
    headers: getHeaders(true),
    body: JSON.stringify(body)
  });
  return result;
}

async function registerBatch() {
  const body = {
    batch_id: document.getElementById('batchId').value.trim(),
    farmer_wallet: document.getElementById('batchFarmerWallet').value.trim(),
    crop_name: document.getElementById('cropName').value.trim(),
    harvest_date: document.getElementById('harvestDate').value,
    is_organic: document.getElementById('batchOrganic').checked,
    quantity_kg: parseFloat(document.getElementById('quantityKg').value) || 0,
    notes: document.getElementById('batchNotes').value.trim()
  };
  const result = await doRequest('/batch/register', {
    method: 'POST',
    headers: getHeaders(true),
    body: JSON.stringify(body)
  });
  return result;
}

async function updateTransport() {
  const body = {
    batch_id: document.getElementById('transportBatchId').value.trim(),
    handler: document.getElementById('handler').value.trim(),
    location: document.getElementById('transportLocation').value.trim(),
    tamper_detected: document.getElementById('tamperDetected').checked,
    timestamp: document.getElementById('timestamp').value
  };
  const result = await doRequest('/batch/update-transport', {
    method: 'POST',
    headers: getHeaders(true),
    body: JSON.stringify(body)
  });
  return result;
}

async function verifyBatch() {
  const batchId = document.getElementById('verifyBatchId').value.trim();
  if (!batchId) throw new Error('Batch ID is required to verify.');
  const result = await doRequest(`/verify/${encodeURIComponent(batchId)}?format=json`, {
    method: 'GET',
    headers: getHeaders(false)
  });
  verifyResult.textContent = '';
  if (result && result.verified !== undefined) {
    verifyResult.textContent = `Batch ${result.batch_id} verified: ${result.verified ? 'Yes' : 'No'}\nCrop: ${result.crop}\nFarmer: ${result.farmer}\nOrganic: ${result.organic}\nTamper: ${result.tamper_detected}\nTrust: ${result.trust_score}`;
  } else if (result && result.error) {
    verifyResult.textContent = `Error: ${result.error}`;
  } else {
    verifyResult.textContent = 'No verify data received.';
  }
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js')
      .then(() => console.log('Service worker registered'))
      .catch(err => console.warn('Service worker registration failed:', err));
  });
}

function wire(selector, fn) {
  const el = document.querySelector(selector);
  if (el) el.addEventListener('click', async () => {
    try {
      await fn();
    } catch (err) {
      responseOutput.textContent = err.message || String(err);
    }
  });
}

wire('#loginBtn', login);
wire('#registerFarmerBtn', registerFarmer);
wire('#registerBatchBtn', registerBatch);
wire('#updateTransportBtn', updateTransport);
wire('#verifyBatchBtn', verifyBatch);
loadSavedKey();
