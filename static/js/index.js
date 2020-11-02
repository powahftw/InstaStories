const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const renderScrapingLogs = (logLines) => {
  const logsNode = document.getElementById('scraping-logs');
  const root = document.createElement('div');
  logLines.forEach((logLine) => {
    const pNode = document.createElement('p');
    pNode.innerText = logLine;
    root.appendChild(pNode);
  });
  logsNode.appendChild(root);
};

const setRadioButtons = (scraperSettings) => {
  document.querySelector(`[name="loop-radio-group"][value="${scraperSettings.loop_mode.toString()}"]`).checked = true;
  document.querySelector(`input[name="media-radio-group"][value="${scraperSettings.media_mode}"]`).checked = true;
  document.querySelector(`input[name="ids-radio-group"][value="${scraperSettings.ids_source}"]`).checked = true;
};

const checkShutdown = async () => {
  const makeStatusRequest = async () => {
    const requestUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`;
    return await (await fetch(requestUrl)).json();
  };

  const CHECK_STATUS_EVERY_MS = 2000;
  const updatePage = async () => {
    const response = await makeStatusRequest();
    if (response.status === 'stopped') {
      location.reload();
    } else {
      setTimeout(updatePage, CHECK_STATUS_EVERY_MS);
    }
  };
  setTimeout(updatePage, CHECK_STATUS_EVERY_MS);
};

const updateCommandButton = (buttonStatus) => {
  const buttonNode = document.getElementById('button-container');
  const root = document.createElement('div');
  const isRunning = buttonStatus == 'running';
  const isShuttingDown = buttonStatus == 'shutdown';
  const commandButton = '<button class="btn" id="command-button"></button>';
  root.innerHTML = commandButton;
  if (isShuttingDown) {
    root.firstChild.classList.add('update-btn');
    root.firstChild.disabled = 'true';
    root.firstChild.innerText = 'updating...';
    checkShutdown();
  } else if (isRunning) {
    root.firstChild.classList.add('stop-btn');
    root.firstChild.value = 'stop';
    root.firstChild.innerText = 'Stop';
  } else {
    root.firstChild.value = 'start';
    root.firstChild.innerText = 'Start';
  }
  buttonNode.appendChild(root);
};

const getScraperStatus = async () => {
  const statusUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`;
  const settingsUrl = `${baseUrl}/${API_PREFIX}/scraper/settings/`;
  const statusResponseData = await (await fetch(statusUrl)).json();
  const settingsResponseData = await (await fetch(settingsUrl)).json();
  const outputNode = document.getElementById('scraping-results');
  renderScrapingLogs(statusResponseData.log_lines);
  updateCommandButton(statusResponseData.status);
  setRadioButtons(settingsResponseData);
  outputNode.innerText = `${statusResponseData.output.scraped_media ?? 0} media scraped`;
};

const startScraping = async () => {
  const userLimit = Number(document.getElementById('user-limit').value);
  const loopMode = document.querySelector('input[name="loop-radio-group"]:checked').value;
  const mediaMode = document.querySelector('input[name="media-radio-group"]:checked').value;
  const idsMode = document.querySelector('input[name="ids-radio-group"]:checked').value;
  const commandType = document.getElementById('command-button').value;
  const requestBody = {
    command: commandType,
    loop_mode: loopMode,
    scraping_args: {
      user_limit: userLimit,
      media_mode: mediaMode,
      ids_source: idsMode,
    },
  };

  const requestUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`;
  const response = await fetch(requestUrl, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  const responseData = await response.json();
  if (responseData.status === 'not logged in') {
    const errorField = document.getElementById('errors');
    errorField.innerText = 'Please login in settings page';
  } else {
    location.reload();
  }
};

const stopScraping = async () => {
  const requestUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`;
  const requestBody = {command: 'stop'};
  await fetch(requestUrl, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  location.reload();
};

const setUpButtonsHandlers = () => {
  const commandButton = document.getElementById('button-container');
  commandButton.addEventListener('click', (e) => {
    if (e.target.value === 'start') {
      startScraping();
    } else {
      stopScraping();
    }
  });
};

window.onload = () => {
  getScraperStatus();
  setUpButtonsHandlers();
};
