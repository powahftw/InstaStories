const API_PREFIX = 'api'
const CONTAINER_ID = 'settings'

const baseUrl = window.location.origin
const fields = ["session_id", "folder_path", "loop_delay_seconds", "loop_variation_percentage", "extra_ids"]

const requestUrl = `${baseUrl}/${API_PREFIX}/settings/`
const loggedinUrl = `${baseUrl}/${API_PREFIX}/loggedin/`


const normalizeExtraIds = (extraIds) => (  // Splits a string of names/numbers into a list when it finds "," or "\n"
    extraIds.split(/,|\n/).map(el => (el.trim()))
)

const checkLogin = async () => {
    const isUserLoggedIn = await (await fetch(loggedinUrl)).json() // Asks the server if the user is logged in
    const loginField = document.getElementById('login_field')
    if (isUserLoggedIn["logged"]) loginField.style.display = 'none'  // If the user is not logged in shows the login form 
    else loginField.style.display = 'block' 
}

const fetchResponseToHtml = async (response) => {  // Sets the placeholders and values in HTML
    if (response.status !== 200) {
        // TODO: Implement a proper error page
        return
    }

    const responseData = await response.json()
    checkLogin()

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

const renderClientSidePage = async () => {  // Makes the GET request and calls fetchResponseToHtml with response as arg
    const response = await fetch(requestUrl).catch(err => { })
    await fetchResponseToHtml(response);
}

const updateSettings = () => {  // Creates a JSON with the updated settings, if a setting is not updated fills it with the old one
    requestJson = {}
    fields.forEach(field => {
        requestJson[field] = document.getElementById(field).value ? document.getElementById(field).value : document.getElementById(field).placeholder
    })
    requestJson["extra_ids"] = [...normalizeExtraIds(requestJson["extra_ids"])]
    postUpdateRequest(requestJson)
}

const updateStatusBar = (res) => {   
    const statusBar = document.getElementById("status_bar")
    res.status === 200 ? statusBar.innerText = "Success!" : statusBar.innerText = "Failure, please try again!"
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
    renderClientSidePage()
} 

const deleteMedia = async () => {
    const deleteMediaUrl = `${baseUrl}/${API_PREFIX}/delete-media/`
    const res = await fetch(deleteMediaUrl)
    renderClientSidePage()
}

const logout = async () => {
    const logoutUrl = `${baseUrl}/${API_PREFIX}/logout/`
    const res = await fetch(logoutUrl)
    renderClientSidePage()
}



const submitBtnListener = () => {  // Event listener for the submit button
    const submitBtn = document.getElementById("submitBtn")
    submitBtn.addEventListener("click", () => {
        updateSettings()
    })
}

const deleteMediaBtnListener = () => {
    const deleteMediaBtn = document.getElementById("deleteMediaBtn")
    deleteMediaBtn.addEventListener("click", () => {
        if(confirm("Are you sure you want to delete all medias?")) {
            deleteMedia()
        }
    })
}

const logoutBtnListener = () => {
    const logoutBtn = document.getElementById("logoutBtn")
    logoutBtn.addEventListener("click", () => {
        if(confirm("Are you sure you want to logout?")) {
            logout()
        }
    })
}

window.onload = () => {
    renderClientSidePage()
    submitBtnListener()
    deleteMediaBtnListener()
    logoutBtnListener()
}