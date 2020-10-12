const API_PREFIX = 'api'

const baseUrl = window.location.origin
const fields = ["session_id", "folder_path", "loop_delay_seconds", "loop_variation_percentage", "extra_ids"]
const requestUrl = `${baseUrl}/${API_PREFIX}/settings/`
const loggedinUrl = `${baseUrl}/${API_PREFIX}/loggedin/`

const normalizeExtraIds = (extraIds) => (  // Splits a string of names/numbers into a list when it finds "," or "\n"
    extraIds.split(/,|\n/).map(el => (el.trim()))
)

const checkLogin = (res) => {
    if (res.session_id) return true
    else return false
}

const fetchResponseToHtml = async (response) => {  // Sets the placeholders and values in HTML
    if (response.status !== 200) {
        // TODO: Implement a proper error page
        return
    }

    const responseData = await response.json()
    const loginField = document.getElementById('login_field')
    const isUserLoggedIn = checkLogin(responseData)
    if (isUserLoggedIn) loginField.style.display = 'none'
    else loginField.style.display = 'block' 

    for (element in responseData) {  // For every element sets its value in HTML
        const elementField = document.getElementById(element)
        if (elementField) {
            if (element === "extra_ids") {
                elementField.value = responseData[element]
            } else {
                elementField.placeholder = responseData[element]
            }
        }
    }
}

const renderSettingsPage = async () => {
    const response = await fetch(requestUrl).catch(err => { })
    await fetchResponseToHtml(response);
}

const updateSettings = () => {  // Creates a JSON with the updated settings, if a setting is not updated fills it with the old one
    let settings = {}
    fields.forEach(field => {
        settings[field] = document.getElementById(field).value || document.getElementById(field).placeholder
    })
    settings["extra_ids"] = [...normalizeExtraIds(settings["extra_ids"])]
    postUpdateRequest(settings)
    renderSettingsPage()
}

const updateStatusBar = (res) => {   
    const statusBar = document.getElementById("status_bar")
    const statusText = res.status === 200 ? "Success!" : "Failure, please try again!"
    statusBar.innerText = statusText
}

const postUpdateRequest = async (payload) => {  // POSTs the request for updating settings
    const res = await fetch(requestUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
          },
        body: JSON.stringify(payload)
    })
    updateStatusBar(res)
    renderSettingsPage()
} 

const deleteMedia = async () => {
    const deleteMediaUrl = `${baseUrl}/${API_PREFIX}/gallery/`
    const res = await fetch(deleteMediaUrl, {
            method: 'DELETE'
        })
    updateStatusBar(res)
    renderSettingsPage()
}

const logout = async () => {
    const logoutUrl = `${baseUrl}/${API_PREFIX}/settings/logout/`
    const res = await fetch(logoutUrl)
    updateStatusBar(res)
    renderSettingsPage()
}

const btnsListener = () => {
    const logoutBtn = document.getElementById("logoutBtn") 
    const deleteMediaBtn = document.getElementById("deleteMediaBtn")
    const submitBtn = document.getElementById("submitBtn")

    logoutBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to logout?")) {
            logout()
        }
    })

    deleteMediaBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to delete all medias?")) {
            deleteMedia()
        }
    })

    submitBtn.addEventListener("click", () => {
        updateSettings()
    })
}

window.onload = () => {
    renderSettingsPage()
    btnsListener()
}
