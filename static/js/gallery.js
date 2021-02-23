const removeTrailingSlash = (string) => {
  return string.endsWith("/") ? string.slice(0, -1) : string;
};

const showAndUpdateSummary = (folderCount, mediaCount) => {
  const summaryEl = document.getElementById("summary");
  let summaryText = "No results";
  if (folderCount && mediaCount) {
    summaryText = `${folderCount} folders - ${mediaCount} medias`;
  } else if (folderCount || mediaCount) {
    summaryText = `${folderCount || mediaCount} ${
      folderCount ? "folders" : "medias"
    }`;
  }
  summaryEl.innerText = summaryText;
  summaryEl.style.display = "block";
};

const renderFolder = (folder) => {
  const liNode = document.createElement("li");
  liNode.innerHTML = `
    <a href="${removeTrailingSlash(window.location.href)}/${folder["id"]}">
        <div class="gallery-folder">
            ${folder["name"]}
        </div>
    </a>`;
  return liNode;
};

const renderMedia = (media) => {
  const liNode = document.createElement("li");
  const tag = media["is_img"] ? "img" : "video";
  const imgUrl = `${removeTrailingSlash(window.location.href)}/${
    media["name"]
  }`;

  liNode.innerHTML = `
        <${tag} ${tag === "video" ? "controls" : ""} src="${imgUrl}" 
            class="rendered-stories">
        </${tag}>`;
  return liNode;
};

const fetchResponseToHtml = async (response) => {
  const root = document.createElement("div");

  if (response.status !== 200) {
    // TODO: Implement a proper error page
    root.append("ERROR");
    return root;
  }

  const responseData = await response.json();
  if (responseData["page_info"]) {
    pageInfo = responseData["page_info"];
    section = pageInfo['section'];
    
    const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

    let breadcrumb = `<a href="/${section}">${capitalize(section)}</a>`;
    if (pageInfo['user_id']) {
      breadcrumb += `/<a href="/${section}/${pageInfo['user_id']}">${pageInfo['display_name']}</a>`;
      if (pageInfo['date']) {
        breadcrumb += `/<span href='#'>${pageInfo['date']}<span>`;
      }
    }
    document.getElementById("title").innerHTML = breadcrumb;
  }

  const sortBasedOnName = (x, y) => {
    return x["name"].localeCompare(y["name"]);
  };
  const data = responseData["items"].sort(sortBasedOnName);
  const renderedItems = document.createElement("ul");

  let folderCount = 0;
  let mediaCount = 0;

  data.forEach((element) => {
    if (element["type"] === "folder") {
      renderedItems.appendChild(renderFolder(element));
      folderCount += 1;
    } else {
      renderedItems.appendChild(renderMedia(element));
      mediaCount += 1;
    }
  });

  showAndUpdateSummary(folderCount, mediaCount);

  root.appendChild(renderedItems);
  return root;
};

const renderClientSidePage = async () => {
  const API_PREFIX = "api";
  const CONTAINER_ID = "gallery";

  const baseUrl = window.location.origin;
  const pathName = window.location.pathname;

  const requestUrl = `${baseUrl}/${API_PREFIX}${pathName}`;

  // Request the data and swallows errors.
  const response = await fetch(requestUrl).catch((err) => {});
  const htmlToAppend = await fetchResponseToHtml(response);

  document.getElementById(CONTAINER_ID).appendChild(htmlToAppend);
};

window.onload = () => {
  renderClientSidePage();
};
