const API_PREFIX = "api";
const baseUrl = window.location.origin;

const composeUserChoicePage = (users) => {
  let pageHtml = "";
  pageHtml += "<p>Users: ${users.length}</p>";
  Array.from(users)
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach(({ name, id }) => {
      pageHtml += `<a href='${baseUrl}/analytics/${id}'>
                    <ul>${name}</ul>
                   </a>`;
    });
  return `<div>${pageHtml}</div>`;
};

const composeStatisticsFromSingleUserJson = (json) => {
  let pageHtml = "";
  const nStories = json.length;
  const storiesOfType = (s, type) => s.filter((j) => j["media_type"] === type).length;
  const nPics = storiesOfType(json, 1);
  const nVideos = storiesOfType(json, 2);
  const lastStory = json[nStories - 1];
  const lastUserName = lastStory["user"]["username"];
  const NGPSLocations = json.filter((j) => "location" in j).length;
  const lastFetchedStoryTime = new Date(lastStory["taken_at"] * 1000)
    .toISOString()
    .slice(0, 19)
    .replace("T", " ");
  const taggedFriends = Array.from(
    new Set(
      json
        .filter((j) => "reel_mentions" in j)
        .flatMap((j) => j["reel_mentions"])
        .filter((j) => j["display_type"] === "mention_username")
        .map((j) => j["user"]["full_name"])
    )
  );
  pageHtml += `<h2>${lastUserName}<h2>`;
  pageHtml += `<p>Last fetched Story at ${lastFetchedStoryTime}</p>`;
  pageHtml += `<p>N:${nStories} STORIES | N: ${nPics} PICS | N: ${nVideos} VIDEOS</p>`;
  pageHtml += `<p>Geotagged ${NGPSLocations} times</p>`;
  pageHtml += `<p>Tagged friends: ${taggedFriends.join(" ")}</p>`;
  return pageHtml;
};

const getAndRenderAnalytics = async () => {
  const baseUrl = window.location.origin;
  const pathName = window.location.pathname;

  const requestUrl = `${baseUrl}/${API_PREFIX}${pathName}`;
  const responseData = await (await fetch(requestUrl)).json();
  const root = document.getElementById("content");

  if (!responseData["all_users"].length && !responseData["user_json_file"]) {
    // TODO: Implement a proper error page
    root.insertAdjacentHTML(
      "afterbegin",
      "<h2 style='color: red;'>Error in the Response</h2>"
    );
    return;
  }

  const isUserChoicePage = responseData["all_users"].length > 0;

  let pageHtml = "";
  if (isUserChoicePage) {
    pageHtml = composeUserChoicePage(responseData["all_users"]);
  } else {
    pageHtml = composeStatisticsFromSingleUserJson(
      responseData["user_json_file"]
    );
  }
  root.insertAdjacentHTML("afterbegin", pageHtml);
};

window.onload = () => {
  getAndRenderAnalytics();
};
