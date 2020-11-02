const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const renderLogs = (logLines) => {
  const logsNode = document.getElementById('logs');
  const root = document.createElement('div');
  logLines.forEach((line) => {
    const pNode = document.createElement('p');
    pNode.innerText = line;
    root.appendChild(pNode);
  });
  logsNode.appendChild(root);
};

const getAndRenderLogs = async () => {
  const requestUrl = `${baseUrl}/${API_PREFIX}/logs`;
  const responseData = await (await fetch(requestUrl)).json();
  renderLogs(responseData['logs']);
};

window.onload = () => {
  getAndRenderLogs();
};
