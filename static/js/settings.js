const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const jsonToIdFields = new Map([
  ['session_id', 'session-id'],
  ['folder_path', 'folder-path'],
  ['loop_delay_seconds', 'loop-delay-seconds'],
  ['loop_variation_percentage', 'loop-variation-percentage'],
  ['extra_ids', 'extra-ids'],
]);
const idToJsonFields = new Map(Array.from(jsonToIdFields, (a) => a.reverse()));

// Splits a string of names/numbers into a list when it finds "," or "\n"
const normalizeExtraIds = (extraIds) => (
  extraIds.split(/,|\n/).map((el) => (el.trim()))
);

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
    loginField.style.display = 'block';
  }

  for (element in responseData) {
    if (responseData.hasOwnProperty(element)) {
      idField = jsonToIdFields.get(element);
      const elementField = document.getElementById(idField);
      if (elementField) {
        if (element === 'extra_ids') {
          elementField.value = responseData[element];
        } else {
          elementField.placeholder = responseData[element];
        }
      }
    }
  }
};

const renderSettingsPage = async () => {
  const requestUrl = `${baseUrl}/${API_PREFIX}/settings/`;
  const response = await fetch(requestUrl).catch((err) => { });
  await fetchResponseToHtml(response);
};

const updateSettings = async () => {
  const settings = {};
  idToJsonFields.forEach((field) => {
    jsonField = field;
    idField = jsonToIdFields.get(field);
    settings[jsonField] = document.getElementById(idField).value || document.getElementById(idField).placeholder;
  });
  settings['extra_ids'] = [...normalizeExtraIds(settings['extra_ids'])];
  await postUpdatedSettings(settings);
  renderSettingsPage();
};

const updateStatusBar = (res) => {
  const statusBar = document.getElementById('status-bar');
  const statusText = res.status === 200 ? 'Success!' : 'Failure, please try again!';
  statusBar.innerText = statusText;
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
  renderSettingsPage();
};

const deleteMedia = async () => {
  const deleteMediaUrl = `${baseUrl}/${API_PREFIX}/gallery/`;
  const res = await fetch(deleteMediaUrl, {
    method: 'DELETE',
  });
  updateStatusBar(res);
  renderSettingsPage();
};

const logout = async () => {
  const logoutUrl = `${baseUrl}/${API_PREFIX}/settings/logout/`;
  const res = await fetch(logoutUrl);
  updateStatusBar(res);
  renderSettingsPage();
};

const setUpButtonsListeners = () => {
  const logoutBtn = document.getElementById('logoutBtn');
  const deleteMediaBtn = document.getElementById('deleteMediaBtn');
  const submitBtn = document.getElementById('submitBtn');

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
};

window.onload = () => {
  renderSettingsPage();
  setUpButtonsListeners();
};
