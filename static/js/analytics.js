const API_PREFIX = "api";
const baseUrl = window.location.origin;
const CHART_CANVAS_ID = "chart";

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
  if (nStories == 0) {
    return "No stories founds!";
  }

  const storiesOfType = (s, type) =>
    s.filter((j) => j["media_type"] === type).length;
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
        .map((j) => j["user"]["full_name"] ?? j["user"]["username"])
        .filter(Boolean) // Remove empty values, if any.
    )
  );
  pageHtml += `<h2>${lastUserName}<h2>`;
  pageHtml += `<p>Last fetched story: ${lastFetchedStoryTime}</p>`;
  pageHtml += `<p>N: ${nStories} Stories | N: ${nPics} Pictures | N: ${nVideos} Videos</p>`;
  pageHtml += `<canvas width="100%" id="${CHART_CANVAS_ID}"></canvas>`;

  if (NGPSLocations > 0) {
    pageHtml += `<p>Geotagged ${NGPSLocations} times</p>`;
  }
  if (taggedFriends.length > 0) {
    pageHtml += `<p>Tagged friends: ${taggedFriends.join(" - ")}</p>`;
  }
  return pageHtml;
};

const renderChartsFromSingleUserJson = (json) => {
  const chartNode = document.getElementById(CHART_CANVAS_ID);
  if (!chartNode) {
    return;
  }

  const pastNMonths = (n) => {
    const now = new Date();
    return Array(n)
      .fill(0)
      .map((x, y) => x + y)
      .map((n) => new Date(now.getFullYear(), now.getMonth() - n))
      .reverse();
  };

  const dateToLabel = (date) =>
    `${date.toLocaleString("en-US", { month: "long" })} ${date.getFullYear()}`;

  const last12Months = pastNMonths(12);
  // Initialize the counter map
  const storyCounter = new Map(last12Months.map((m) => [dateToLabel(m), 0]));
  json.forEach((j) => {
    const timestamp = new Date(j["taken_at"] * 1000);
    const date = dateToLabel(timestamp);
    if (storyCounter.has(date)) {
      storyCounter.set(date, storyCounter.get(date) + 1);
    }
  });
  const ctx = chartNode.getContext("2d");
  const getPurplePalette = (opacity = 1) => `rgba(153, 102, 255, ${opacity})`;

  const _ = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [...storyCounter.keys()],
      datasets: [
        {
          label: "# of Stories",
          data: [...storyCounter.values()],
          backgroundColor: getPurplePalette(0.2),
          borderColor: getPurplePalette(),
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
          },
        ],
      },
    },
  });
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

  if (isUserChoicePage) {
    const pageHtml = composeUserChoicePage(responseData["all_users"]);
    root.insertAdjacentHTML("afterbegin", pageHtml);
  } else {
    userJsonFile = responseData["user_json_file"];
    const pageHtml = composeStatisticsFromSingleUserJson(userJsonFile);
    root.insertAdjacentHTML("afterbegin", pageHtml);
    renderChartsFromSingleUserJson(userJsonFile);
  }
};

window.onload = () => {
  getAndRenderAnalytics();
};
