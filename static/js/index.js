const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const setScrapingLogs = (logs) => {
    const logsNode = document.getElementById('scraping-logs')
    for (i in logs) {
        pNode = document.createElement('p')
        pNode.innerText = logs[i]
        logsNode.appendChild(pNode)
    }
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
        if (el.value === scraperSettings['media_mode'].toString()) {
            el.checked = true
        }
    })

    idsModeNode.forEach((el) => {
        if (el.value === scraperSettings['ids_source'].toString()) {
            el.checked = true
        }
    })
}

const checkShutdown = async () => {
    const timeInterval = 2000
    const makeRequest = async () => {
        const requestUrl = `${baseUrl}/${API_PREFIX}/status/`;
        const responseData = await (await fetch(requestUrl)).json()
        return responseData
    }

    const updatePage = async () => {
        try {
            const response = await makeRequest()
            if (response['status'] === "stopped") {
                location.reload()
            } else {
                setTimeout(updatePage, timeInterval)
            }
         } catch {
             location.reload()
         }
    }

    setTimeout(updatePage, timeInterval)
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
    const requestUrl = `${baseUrl}/${API_PREFIX}/index/`;
    const responseData =  await (await fetch(requestUrl)).json()
    const outputNode = document.getElementById('scraping-results')
    setScrapingLogs(responseData['log_lines'])
    setRadioButtons(responseData['scraper_settings'])
    updateCommandButton(responseData['scraper_status'])
    outputNode.innerText = `${responseData['output']['scraped_media'] ?? 0} media scraped`
}

const startScraping = async () => {
    const userLimit = Number(document.getElementById('user-limit').value)
    const loopMode = document.querySelector('input[name="loop-radio-group"]:checked').value
    const mediaMode = document.querySelector('input[name="media-radio-group"]:checked').value
    const idsMode = document.querySelector('input[name="ids-radio-group"]:checked').value
    const commandType = document.getElementById('command-button').value
    const errorField = document.getElementById('errors')
    const requestBody = {
        "command": commandType,
        "user_limit": userLimit,
        "loop_mode": loopMode,
        "media_mode": mediaMode,
        "ids_source": idsMode
    }
    const requestUrl = `${baseUrl}/${API_PREFIX}/index/`
    const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    const responseData = await response.json()
    if (responseData['status'] === "not logged in"){
        errorField.innerText = "Please login in settings page"
        return
    }
    location.reload()
}

const stopScraping = async () => {
    const requestUrl = `${baseUrl}/${API_PREFIX}/index/`
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
