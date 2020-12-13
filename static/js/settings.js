const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const extraIDs = new Set();

const jsonToIdFields = new Map([
  ['session_id', 'session-id'],
  ['folder_path', 'folder-path'],
  ['loop_delay_seconds', 'loop-delay-seconds'],
  ['loop_variation_percentage', 'loop-variation-percentage'],
  ['extra_ids', 'extra-ids'],
]);
const idToJsonFields = new Map(Array.from(jsonToIdFields, (a) => a.reverse()));

const displayWarningUnsavedChanges = (isActive) => {
  const errors = document.getElementById('errors');
  if (isActive) {
    errors.innerText = 'Attention! Unsaved changes';
  } else {
    errors.innerText = '';
  }
};

const deleteExtraID = (extraID) => {
  if (extraIDs.delete(extraID)) {
    displayWarningUnsavedChanges(true);
    renderExtraIDs();
  };
};

const addExtraID = (extraID) => {
  if ((extraID.trim().length > 0) && !extraIDs.has(extraID)) {
    extraIDs.add(extraID);
    displayWarningUnsavedChanges(true);
    renderExtraIDs();
  };
};

const renderExtraIDs = () => {
  const root = document.getElementById('extra-ids');
  const extraIDsNode = document.createElement('div');
  root.innerHTML = '';
  extraIDsNode.classList.add('extra-ids-list');
  extraIDs.forEach((id) => {
    extraIDsNode.innerHTML += `
            <div class="extra-id-container">
              <div class="extra-id-name">
                ${id}
              </div>
              <div class="delete-extra-id" onclick="deleteExtraID('${id}')">X</div>
            </div>`;
  });
  root.appendChild(extraIDsNode);
};

// Sets the placeholders and values in HTML
const fetchResponseToHtml = async (response) => {
  if (response.status !== 200) {
    // TODO: Implement a proper error page
    return;
  }

  const responseData = await response.json();
  const loginField = document.getElementById('login-field');
  const isUserLoggedIn = ('session_id' in responseData);
  if (isUserLoggedIn) {
    loginField.style.display = 'none';
  } else {
    loginField.style.display = 'flex';
  }

  for (element in responseData) {
    if (responseData.hasOwnProperty(element)) {
      idField = jsonToIdFields.get(element);
      const elementField = document.getElementById(idField);
      if (elementField) {
        if (element === 'extra_ids') {
          responseData[element].forEach((id) => extraIDs.add(id));
          renderExtraIDs();
        } else {
          elementField.placeholder = responseData[element];
        }
      }
    }
  }
};

const getAndRenderSettingsPage = async () => {
  const settingsRequestUrl = `${baseUrl}/${API_PREFIX}/settings/`;
  const diskUsageRequestUrl = `${baseUrl}/${API_PREFIX}/settings/diskusage`;
  const [
    settingsResponse,
    diskUsageResponse,
  ] = await Promise.all([
    fetch(settingsRequestUrl),
    fetch(diskUsageRequestUrl),
  ]);

  await fetchResponseToHtml(settingsResponse);
  await renderDiskUsage(diskUsageResponse);
};

const renderDiskUsage = async (res) => {
  const responseData = await res.json();
  const rootNode = document.getElementById('disk-usage');
  rootNode.innerHTML = `<p>Disk used space: ${responseData.used_space}/${responseData.total_space} GiB <br>
                 Disk free space: ${responseData.free_space}/${responseData.total_space} GiB
                 </p>`;
};

const updateSettings = async () => {
  const settings = {};
  idToJsonFields.forEach((field) => {
    jsonField = field;
    idField = jsonToIdFields.get(field);
    settings[jsonField] = document.getElementById(idField).value || document.getElementById(idField).placeholder;
  });
  settings['extra_ids'] = Array.from(extraIDs);
  await postUpdatedSettings(settings);
  getAndRenderSettingsPage();
  displayWarningUnsavedChanges(false);
};

const updateStatusBar = (res) => {
  const statusBar = document.getElementById('status-bar');
  const statusText = res.status === 200 ? 'Success!' : 'Failure, please try again!';
  statusBar.innerText = statusText;

  const hideStatusBar = (statusBar) => {
    statusBar.innerText = '';
  };

  setTimeout(() => hideStatusBar(statusBar), 5000);
};

const postUpdatedSettings = async (payload) => { // POSTs the request for updating settings
  const requestUrl = `${baseUrl}/${API_PREFIX}/settings/`;
  const res = await fetch(requestUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  updateStatusBar(res);
  getAndRenderSettingsPage();
};

const deleteMedia = async () => {
  const deleteMediaUrl = `${baseUrl}/${API_PREFIX}/gallery/`;
  const res = await fetch(deleteMediaUrl, {
    method: 'DELETE',
  });
  updateStatusBar(res);
  getAndRenderSettingsPage();
};

const logout = async () => {
  const logoutUrl = `${baseUrl}/${API_PREFIX}/settings/logout/`;
  const res = await fetch(logoutUrl);
  updateStatusBar(res);
  getAndRenderSettingsPage();
};

const setUpButtonsListeners = () => {
  const logoutBtn = document.getElementById('logoutBtn');
  const deleteMediaBtn = document.getElementById('deleteMediaBtn');
  const submitBtn = document.getElementById('submitBtn');
  const addExtraIDBtn = document.getElementById('add-extra-id');

  logoutBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to logout?')) {
      logout();
    }
  });

  deleteMediaBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to delete all medias?')) {
      deleteMedia();
    }
  });

  submitBtn.addEventListener('click', () => {
    updateSettings();
  });

  addExtraIDBtn.addEventListener('click', () => {
    const extraID = document.getElementById('new-extra-id').value;
    addExtraID(extraID);
  });
};

window.onload = () => {
  getAndRenderSettingsPage();
  setUpButtonsListeners();
};
