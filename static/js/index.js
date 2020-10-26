const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const setScrapingLogs = (logs) => {
    const logsNode = document.getElementById('scraping-logs')
    logs.forEach((el) => {
        pNode = document.createElement('p')
        pNode.innerText = el
        logsNode.appendChild(pNode) 
    });
}

const setRadioButtons = (scraperSettings) => {
    const loopModeNode = document.querySelectorAll('input[name="loop-radio-group"]')
    const mediaModeNode = document.querySelectorAll('input[name="media-radio-group"]')
    const idsModeNode = document.querySelectorAll('input[name="ids-radio-group"]')
    loopModeNode.forEach( (el) => {
        if (el.value === scraperSettings['loop_mode'].toString()) {
            el.checked = true
        }
    })

    mediaModeNode.forEach((el) => {
        if (el.value === scraperSettings['media_mode']) {
            el.checked = true
        }
    })

    idsModeNode.forEach((el) => {
        if (el.value === scraperSettings['ids_source']) {
            el.checked = true
        }
    })
}

const checkShutdown = async () => {
    const makeStatusRequest = async () => {
        const requestUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`;
        return await (await fetch(requestUrl)).json()
    }

    const checkStatusEveryMs = 2000
    const updatePage = async () => {
        try {
            const response = await makeStatusRequest()
            if (response['status'] === "stopped") {
                location.reload()
            } else {
                setTimeout(updatePage, checkStatusEveryMs)
            }
         } catch {
             location.reload()
         }
    }
    setTimeout(updatePage, checkStatusEveryMs)
}

const updateCommandButton = (buttonStatus) => {
    const commandButton = document.getElementById('command-button')
    if (buttonStatus === "running") {
        commandButton.disabled = false
        commandButton.classList = "btn stop-btn"
        commandButton.innerText = "STOP"
        commandButton.value = "stop"
    } else if (buttonStatus === "shutdown") {
        commandButton.disabled = true
        commandButton.classList = "btn update-btn"
        commandButton.innerText = "updating..."
        checkShutdown()
    } else {
        commandButton.disabled = false
        commandButton.classList = "btn start-btn"
        commandButton.innerText = "START"
        commandButton.value = "start"
    }
}

const getScraperStatus = async () => {
    const statusUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`;
    const settingsUrl = `${baseUrl}/${API_PREFIX}/scraper/settings/`;
    const statusResponseData =  await (await fetch(statusUrl)).json()
    const settingsResponseData =  await (await fetch(settingsUrl)).json()
    const outputNode = document.getElementById('scraping-results')
    setScrapingLogs(statusResponseData['log_lines'])
    setRadioButtons(settingsResponseData)
    updateCommandButton(statusResponseData['status'])
    outputNode.innerText = `${statusResponseData['output']['scraped_media'] ?? 0} media scraped`
}

const startScraping = async () => {
    const userLimit = Number(document.getElementById('user-limit').value)
    const loopMode = document.querySelector('input[name="loop-radio-group"]:checked').value
    const mediaMode = document.querySelector('input[name="media-radio-group"]:checked').value
    const idsMode = document.querySelector('input[name="ids-radio-group"]:checked').value
    const commandType = document.getElementById('command-button').value
    const requestBody = {
        "command": commandType,
        "loop_mode": loopMode,
        "scraping_args": {
            "user_limit": userLimit,
            "media_mode": mediaMode,
            "ids_source": idsMode
        }
    }
    const requestUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`
    const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })

    const responseData = await response.json()
    if (responseData['status'] === "not logged in"){
        const errorField = document.getElementById('errors')
        errorField.innerText = "Please login in settings page"
        return
    }
    location.reload()
}

const stopScraping = async () => {
    const requestUrl = `${baseUrl}/${API_PREFIX}/scraper/status/`
    const requestBody = {'command': 'stop'}
    const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    location.reload()
}

const setUpButtonsHandlers = () => {
    const commandButton = document.getElementById('command-button')
    commandButton.addEventListener('click', () => {
        if (commandButton.value == "start") {
            startScraping()
        } else {
            stopScraping()
        }
    })
}

window.onload = () => {
    getScraperStatus()
    setUpButtonsHandlers()
}
