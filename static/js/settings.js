const API_PREFIX = "api";
const baseUrl = window.location.origin;

const extraIDs = new Set();
const blacklistedIDs = new Set();

const jsonToIdFields = new Map([
  ["session_id", "session-id"],
  ["folder_path", "folder-path"],
  ["loop_delay_seconds", "loop-delay-seconds"],
  ["loop_variation_percentage", "loop-variation-percentage"],
  ["extra_ids", "extra-ids"],
  ["blacklisted_ids", "blacklisted-ids"],
]);
const idToJsonFields = new Map(Array.from(jsonToIdFields, (a) => a.reverse()));

const displayWarningUnsavedChanges = (isActive) => {
  const errors = document.getElementById("errors");
  errors.innerText = isActive ? "Attention! Unsaved changes" : "";
};

const deleteID = (id, listType) => {
  const IDs = listType == "extraIDs" ? extraIDs : blacklistedIDs;

  if (IDs.delete(id)) {
    displayWarningUnsavedChanges(true);
    renderIDs(listType);
  }
};

const addID = (id, listType) => {
  const IDs = listType == "extraIDs" ? extraIDs : blacklistedIDs;

  if (id.trim().length > 0 && !IDs.has(id)) {
    IDs.add(id);
    displayWarningUnsavedChanges(true);
    renderIDs(listType);
  }
};

const renderIDs = (listType) => {
  if (listType === "extraIDs") {
    var IDs = extraIDs;
    var nodeName = "extra-ids";
    var containerName = "extra-id-container";
  } else if (listType === "blacklistedIDs") {
    var IDs = blacklistedIDs;
    var nodeName = "blacklisted-ids";
    var containerName = "blacklisted-id-container";
  }

  const root = document.getElementById(nodeName);
  const IDsNode = document.createElement("div");
  root.innerHTML = "";
  IDsNode.classList.add("extra-ids-list");
  IDs.forEach((id) => {
    IDsNode.innerHTML += `
            <div class="${containerName}">
              <div class="extra-id-name">
                ${id}
              </div>
              <div class="delete-extra-id" onclick="deleteID('${id}', '${listType}')">X</div>
            </div>`;
  });
  root.appendChild(IDsNode);
};

// Sets the placeholders and values in HTML
const fetchResponseToHtml = async (response) => {
  if (response.status !== 200) {
    // TODO: Implement a proper error page
    return;
  }

  const responseData = await response.json();
  const loginField = document.getElementById("login-field");
  const logoutField = document.getElementById("logoutBtn");
  const isUserLoggedIn = "session_id" in responseData;
  if (isUserLoggedIn) {
    loginField.style.display = "none";
    logoutField.style.display = "block";
  } else {
    loginField.style.display = "flex";
    logoutField.style.display = "none";
  }

  for (element in responseData) {
    if (responseData.hasOwnProperty(element)) {
      idField = jsonToIdFields.get(element);
      const elementField = document.getElementById(idField);
      if (elementField) {
        if (element === "extra_ids") {
          responseData[element].forEach((id) => extraIDs.add(id));
          renderIDs("extraIDs");
        } else if (element === "blacklisted_ids") {
          responseData[element].forEach((id) => blacklistedIDs.add(id));
          renderIDs("blacklistedIDs");
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
  const [settingsResponse, diskUsageResponse] = await Promise.all([
    fetch(settingsRequestUrl),
    fetch(diskUsageRequestUrl),
  ]);

  await fetchResponseToHtml(settingsResponse);
  await renderDiskUsage(diskUsageResponse);
};

const renderDiskUsage = async (res) => {
  const responseData = await res.json();
  const rootNode = document.getElementById("disk-usage");
  rootNode.innerHTML = `<p>Disk used space: ${responseData.used_space}/${responseData.total_space} GiB <br>
                 Disk free space: ${responseData.free_space}/${responseData.total_space} GiB
                 </p>`;
};

const updateSettings = async () => {
  const settings = {};
  idToJsonFields.forEach((jsonField) => {
    idField = jsonToIdFields.get(jsonField);
    settings[jsonField] =
      document.getElementById(idField).value ||
      document.getElementById(idField).placeholder;
  });
  settings["extra_ids"] = Array.from(extraIDs);
  settings["blacklisted_ids"] = Array.from(blacklistedIDs);
  await postUpdatedSettings(settings);
  getAndRenderSettingsPage();
  displayWarningUnsavedChanges(false);
};

const updateStatusBar = (res) => {
  const HIDE_STATUS_AFTER_MS = 2000;
  const statusBar = document.getElementById("status-bar");
  const statusText =
    res.status === 200 ? "Success!" : "Failure, please try again!";
  statusBar.innerText = statusText;

  const hideStatusBar = (statusBar) => {
    statusBar.innerText = "";
  };

  setTimeout(() => hideStatusBar(statusBar), HIDE_STATUS_AFTER_MS);
};

const postUpdatedSettings = async (payload) => {
  // POSTs the request for updating settings
  const requestUrl = `${baseUrl}/${API_PREFIX}/settings/`;
  const res = await fetch(requestUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  updateStatusBar(res);
  getAndRenderSettingsPage();
};

const deleteMedia = async () => {
  const deleteMediaUrl = `${baseUrl}/${API_PREFIX}/gallery/`;
  const res = await fetch(deleteMediaUrl, {
    method: "DELETE",
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
  const logoutBtn = document.getElementById("logoutBtn");
  const deleteMediaBtn = document.getElementById("deleteMediaBtn");
  const submitBtn = document.getElementById("submitBtn");
  const addExtraIDBtn = document.getElementById("add-extra-id");
  const addBlacklistedIDBtn = document.getElementById("add-blacklisted-id");

  logoutBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to logout?")) {
      logout();
    }
  });

  deleteMediaBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete all medias?")) {
      deleteMedia();
    }
  });

  submitBtn.addEventListener("click", () => {
    updateSettings();
  });

  addExtraIDBtn.addEventListener("click", () => {
    const extraID = document.getElementById("new-extra-id").value;
    addID(extraID, "extraIDs");
  });

  addBlacklistedIDBtn.addEventListener("click", () => {
    const blacklistedID = document.getElementById("blacklist-id").value;
    addID(blacklistedID, "blacklistedIDs");
  });

  const changingInputs = [
    document.getElementById("loop-variation-percentage"),
    document.getElementById("loop-delay-seconds"),
    document.getElementById("folder-path"),
  ];
  changingInputs.forEach((input) => {
    input.addEventListener("input", () => {
      displayWarningUnsavedChanges(true);
    });
  });
};

window.onload = () => {
  getAndRenderSettingsPage();
  setUpButtonsListeners();
};
