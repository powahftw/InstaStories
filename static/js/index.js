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

const setDropdown = (scraperSettings) => {
  document.querySelector(`select[id="loop-mode"]`).value = scraperSettings.loop_mode;
  document.querySelector(`select[id="scraping-mode"]`).value = scraperSettings.media_mode;
  document.querySelector(`select[id="ids-source"]`).value = scraperSettings.ids_source;
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
  const commandButton = '<button class="button" id="command-button"></button>';
  root.innerHTML = commandButton;
  if (isShuttingDown) {
    root.firstChild.classList.add('update-button');
    root.firstChild.disabled = 'true';
    root.firstChild.innerText = 'updating...';
    checkShutdown();
  } else if (isRunning) {
    root.firstChild.classList.add('stop-button');
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
  const imageOutputNode = document.getElementById('image-scraping-results');
  const videoOutputNode = document.getElementById('video-scraping-results');
  renderScrapingLogs(statusResponseData.log_lines);
  updateCommandButton(statusResponseData.status);
  setDropdown(settingsResponseData);
  imageOutputNode.innerText = `${statusResponseData.output.scraped_images ?? 0}`;
  videoOutputNode.innerText = `${statusResponseData.output.scraped_videos ?? 0}`;
};

const startScraping = async () => {
  const userLimit = Number(document.getElementById('user-limit').value);
  const loopMode = document.querySelector(`select[id="loop-mode"]`).value;
  const mediaMode = document.querySelector(`select[id="scraping-mode"]`).value;
  const idsMode = document.querySelector(`select[id="ids-source"]`).value;
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
