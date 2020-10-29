const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const renderLogs = (logs) => {
    const logsNode = document.getElementById('logs');
    const root = document.createElement('div')
    logs.forEach( (el) => {
        const pNode = document.createElement('p');
        pNode.innerText = el
        root.appendChild(pNode)
    })
    logsNode.appendChild(root)
}

const getLogs = async () => {
    const requestUrl = `${baseUrl}/${API_PREFIX}/logs`;
    const responseData = await (await fetch(requestUrl)).json();
    renderLogs(responseData['logs']);
}

window.onload = () => {
    getLogs();
};
