const removeTrailingSlash = (string) => {
  return string.endsWith('/') ? string.slice(0, -1) : string;
};

const renderFolder = (folder) => {
  const liNode = document.createElement('li');
  liNode.innerHTML = `
    <a href="${removeTrailingSlash(window.location.href)}/${folder['name']}">
        <div class="gallery-folders">
            ${folder['name']}
        </div>
    </a>`;
  return liNode;
};

const renderMedia = (media) => {
  const liNode = document.createElement('li');
  const tag = media['is_img'] ? 'img': 'video';
  const imgUrl = `${removeTrailingSlash(window.location.href)}/${media['name']}`;

  liNode.innerHTML = `
        <${tag} ${tag === 'video' ? 'controls' : ''} src="${imgUrl}" 
            class="rendered-stories">
        </${tag}>`;
  return liNode;
};

const fetchResponseToHtml = async (response) => {
  const root = document.createElement('div');

  if (response.status !== 200) {
    // TODO: Implement a proper error page
    root.append('ERROR');
    return root;
  }

  const responseData = await response.json();
  const data = responseData['items'];
  const renderedItems = document.createElement('ul');

  data.forEach((element) => {
    if (element['type'] === 'folder') {
      renderedItems.appendChild(renderFolder(element));
    } else {
      renderedItems.appendChild(renderMedia(element));
    }
  });

  root.appendChild(renderedItems);
  return root;
};


const renderClientSidePage = async () => {
  const API_PREFIX = 'api';
  const CONTAINER_ID = 'gallery';

  const baseUrl = window.location.origin;
  const pathName = window.location.pathname;

  const requestUrl = `${baseUrl}/${API_PREFIX}${pathName}`;

  // Request the data and swallows errors.
  const response = await fetch(requestUrl).catch((err) => { });
  const htmlToAppend = await fetchResponseToHtml(response);

  document.getElementById(CONTAINER_ID).appendChild(htmlToAppend);
};

window.onload = () => {
  renderClientSidePage();
};
