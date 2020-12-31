const API_PREFIX = 'api';
const baseUrl = window.location.origin;

const renderLogs = (logLines) => {
  const logsNode = document.getElementById('logs');
  logsNode.innerHTML = '';
  const root = document.createElement('div');
  logLines.forEach((line) => {
    const pNode = document.createElement('p');
    pNode.innerText = line;
    root.appendChild(pNode);
  });
  logsNode.appendChild(root);
};

const renderNav = (pageN, maxPage) => {
  const paginationNode = document.getElementById('pagination');
  paginationNode.innerHTML = ''

  if (maxPage == 1 || maxPage == 0) {
    return; // Don't display pagination on log files that fit in a single page.
  }
  const root = document.createElement('div');
  decrease = document.createElement('button');
  decrease.innerText = '<';
  decrease.addEventListener('click', () => getAndRenderLogs(pageN - 1));
  root.append(decrease);
  root.append(document.createTextNode(`${pageN} / ${maxPage}`));
  increase = document.createElement('button');
  increase.innerText = '>';
  increase.addEventListener('click', () => getAndRenderLogs(pageN + 1));
  root.append(increase);
  if(pageN <= 1) {
    decrease.style.visibility = 'hidden'
  } else if (pageN >= maxPage) {
    increase.style.visibility = 'hidden'
  }
  paginationNode.append(root);
}

const getAndRenderLogs = async (page = 1) => {
  const requestUrl = `${baseUrl}/${API_PREFIX}/logs/${page}`;
  const responseData = await (await fetch(requestUrl)).json();
  renderNav(responseData['page'], responseData['max_page']);
  renderLogs(responseData['logs']);
};

window.onload = () => {
  getAndRenderLogs();
};
