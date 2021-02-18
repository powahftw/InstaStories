const API_PREFIX = "api";
const baseUrl = window.location.origin;

const getNColours = (n) => {
  const defaultPaletteSize = CHARTS_DEFAULTS_COLORS.length;
  const repeatPaletteNTimes = Math.ceil(n / defaultPaletteSize);
  return new Array(repeatPaletteNTimes)
    .fill(CHARTS_DEFAULTS_COLORS)
    .flat()
    .slice(0, n);
};

const CHARTS_DEFAULTS_COLORS = [
  "rgba(255, 99, 132, 0.2)",
  "rgba(54, 162, 235, 0.2)",
  "rgba(255, 206, 86, 0.2)",
  "rgba(75, 192, 192, 0.2)",
  "rgba(153, 102, 255, 0.2)",
  "rgba(255, 159, 64, 0.2)",
];

const composeUserChoicePage = (users) => {
  let pageHtml = "";
  pageHtml += `<p>Users: ${users.length}</p>`;
  pageHtml += "<div class='analitics-users'>";
  Array.from(users)
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach(({ name, id }) => {
      pageHtml += `<a href='${baseUrl}/analytics/${id}'>
                    <ul>${name}</ul>
                   </a>`;
    });
  pageHtml += "</div>";
  return `<div class='analitics-wrapper'>${pageHtml}</div>`;
};

const taggedFriendsFromJson = (json) => {
  return json
    .filter((j) => "reel_mentions" in j)
    .flatMap((j) => j["reel_mentions"])
    .filter((j) => j["display_type"] === "mention_username")
    .map((j) => j["user"]["full_name"] ?? j["user"]["username"])
    .filter(Boolean); // Remove empty values, if any.
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
  const taggedFriends = Array.from(new Set(taggedFriendsFromJson(json)));
  pageHtml += `<h2>${lastUserName}</h2>`;
  pageHtml += `<p>Last fetched story: ${lastFetchedStoryTime}</p>`;
  pageHtml += `<p>N: ${nStories} Stories | N: ${nPics} Pictures | N: ${nVideos} Videos</p>`;
  pageHtml += `<canvas width="100%" id="chart-media"></canvas>`;
  pageHtml += `<canvas width="100%" id="chart-hourly-freq"></canvas>`;

  if (NGPSLocations > 0) {
    pageHtml += `<p>Geotagged ${NGPSLocations} times</p>`;
  }
  if (taggedFriends.length > 0) {
    pageHtml += `<p>Tagged friends: ${taggedFriends.join(" - ")}</p>`;
    pageHtml += `<canvas width="100%" id="chart-tagged"></canvas>`;
  }
  return pageHtml;
};

const createBarGraph = (ctx, label, labels, data) => {
  const getPurplePalette = (opacity = 1) => `rgba(153, 102, 255, ${opacity})`;

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: [...labels],
      datasets: [
        {
          label: label,
          data: [...data],
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
const renderMediaCountGraphFromJson = (json) => {
  const mediaCountGraph = document.getElementById("chart-media");

  if (!mediaCountGraph) {
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
  const mediaCountCtx = mediaCountGraph.getContext("2d");

  createBarGraph(
    mediaCountCtx,
    "# of Stories",
    storyCounter.keys(),
    storyCounter.values()
  );
};

const renderHourlyFrequencyGraphFromJson = (json) => {
  const hourlyFrequencyGraph = document.getElementById("chart-hourly-freq");
  if (!hourlyFrequencyGraph) {
    return;
  }

  const hourlyFrequencyGraphCtx = hourlyFrequencyGraph.getContext("2d");

  const all24Hours = Array(24)
    .fill(0)
    .map((x, y) => x + y);

  // Initialize the counter map
  const hourlyCounter = new Map(all24Hours.map((m) => [m.toString(), 0]));

  json.forEach((j) => {
    const hour = new Date(j["taken_at"] * 1000).getHours().toString();
    if (hourlyCounter.has(hour)) {
      hourlyCounter.set(hour, hourlyCounter.get(hour) + 1);
    }
  });

  createBarGraph(
    hourlyFrequencyGraphCtx,
    "# of Stories by hours",
    hourlyCounter.keys(),
    hourlyCounter.values()
  );
};

const renderTaggedFriendsGraphFromJson = (json) => {
  const taggedFriendsGraph = document.getElementById("chart-tagged");
  if (!taggedFriendsGraph) {
    return;
  }

  const taggedFriendsCtx = taggedFriendsGraph.getContext("2d");

  const tags = taggedFriendsFromJson(json);
  const tagsCounter = new Map();
  tags.forEach((tag) => tagsCounter.set(tag, (tagsCounter.get(tag) || 0) + 1));

  new Chart(taggedFriendsCtx, {
    type: "pie",
    data: {
      labels: [...tagsCounter.keys()],
      datasets: [
        {
          label: "Tags",
          data: [...tagsCounter.values()],
          backgroundColor: getNColours(tagsCounter.size),
        },
      ],
    },
    options: {
      responsive: true,
    },
  });
};

const renderChartsFromSingleUserJson = (json) => {
  renderMediaCountGraphFromJson(json);
  renderHourlyFrequencyGraphFromJson(json);
  renderTaggedFriendsGraphFromJson(json);
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
