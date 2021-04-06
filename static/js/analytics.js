const API_PREFIX = "api";
const baseUrl = window.location.origin;
const pathName = window.location.pathname;

const DEFAULT_LOOKBACK_MONTHS = 3;

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
  pageHtml += "<div class='analytics-users'>";
  Array.from(users)
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach(({ name, id }) => {
      pageHtml += `<a href='${baseUrl}/analytics/${id}'>
                    <div class="user-preview">${name}</div>
                   </a>`;
    });
  pageHtml += "</div>";
  return `<div class='analytics-wrapper'>${pageHtml}</div>`;
};

const taggedFriendsFromJson = (json) => {
  return json
    .filter((j) => "reel_mentions" in j)
    .flatMap((j) => j["reel_mentions"])
    .filter((j) => j["display_type"] === "mention_username")
    .map((j) => j["user"]["full_name"] ?? j["user"]["username"])
    .filter(Boolean); // Remove empty values, if any.
};

const hashtagsFromJson = (json) => {
  return json
    .filter((j) => "story_hashtags" in j)
    .flatMap((j) => j["story_hashtags"])
    .map((j) => j["hashtag"]["name"])
    .filter(Boolean);
};

const composeStatisticsFromSingleUserJson = (json) => {
  let pageHtml = "";

  const composeChartContainer = (header, body) =>
    `<div class="analytics-box">
      <div class="analytics-box-header">${header}</div>
      <div class="analytics-box-body">${body}</div>
    </div>`;

  const composeUserDetailsBarBox = (header, body) =>
    `<div class="user-details-box">
      <div class="user-details-box-header">${header}</div>
      <div class="user-details-box-body">${body}</div>
    </div>`;

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
  const hashtags = Array.from(new Set(hashtagsFromJson(json)));

  const selectedUserStoriesInfo = {
    "Username": lastUserName,
    "Last fetched story": lastFetchedStoryTime,
    "Number of stories": nStories,
    "Number of pictures": nPics,
    "Number of videos": nVideos,
  };

  let selectedUserInfoBar = `<div class="user-details-bar">`;
  for (const [fieldName, fieldValue] of Object.entries(
    selectedUserStoriesInfo
  )) {
    selectedUserInfoBar += composeUserDetailsBarBox(fieldName, fieldValue);
  }
  selectedUserInfoBar += `</div>`;

  const createCanvasFromId = (id) =>
    `<canvas width="100%" id="${id}"></canvas>`;
  const charts = {
    "Media chart": createCanvasFromId("chart-media"),
    "Frequency chart": createCanvasFromId("chart-hourly-freq"),
    ...(hashtags.length && {
      "Hashtags chart": createCanvasFromId("chart-hashtags"),
    }),
    ...(taggedFriends.length && {
      "Tags chart": createCanvasFromId("chart-tagged"),
    }),
  };
  let analyticsBox = `<div class="analytics-box-container">`;
  for (const [chartName, chartCanvas] of Object.entries(charts)) {
    analyticsBox += composeChartContainer(chartName, chartCanvas);
  }
  analyticsBox += `</div>`;

  pageHtml += selectedUserInfoBar + analyticsBox;

  if (NGPSLocations > 0) {
    pageHtml += `<p>Geotagged ${NGPSLocations} times</p>`;
  }
  return pageHtml;
};

const createBarGraph = (ctx, label, labels, data) => {
  const getPurplePalette = (opacity = 1) => `rgba(153, 102, 255, ${opacity})`;
  const getGreyPalette = (opacity = 1) => `rgba(255, 255, 255, ${opacity})`;

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
        xAxes: [
          {
            gridLines: {
              display: true,
              color: getGreyPalette(0.1),
            },
          },
        ],
        yAxes: [
          {
            gridLines: {
              display: true,
              color: getGreyPalette(0.1),
              zeroLineColor: getGreyPalette(0.3),
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

const renderHashtagsGraphFromJson = (json) => {
  const hashtagsGraph = document.getElementById("chart-hashtags");
  if (!hashtagsGraph) {
    return;
  }

  const hashtagsCtx = hashtagsGraph.getContext("2d");
  const hashtags = hashtagsFromJson(json);
  const hashtagsCounter = new Map();
  hashtags.forEach((hashtag) => hashtagsCounter.set(hashtag, (hashtagsCounter.get(hashtag) || 0) + 1));

  new Chart(hashtagsCtx, {
    type: "pie",
    data: {
      labels: [...hashtagsCounter.keys()],
      datasets: [
        {
          label: "Hashtags",
          data: [...hashtagsCounter.values()],
          backgroundColor: getNColours(hashtags.length),
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
  renderHashtagsGraphFromJson(json);
};

const updateDatePicker = (startDateTimestamp, endDateTimestamp) => {
  const startDate = new Date(startDateTimestamp).toISOString().split("T")[0];
  const endDate = new Date(endDateTimestamp).toISOString().split("T")[0];
  document.getElementById("start-date").value = startDate;
  document.getElementById("end-date").value = endDate;
};

const getDateIntervalAndUpdateDatePicker = () => {
  const startDateField = document.getElementById("start-date").value;
  const endDateField = document.getElementById("end-date").value;
  const currentDate = new Date();
  let endDateTimestamp = endDateField
    ? new Date(endDateField).getTime()
    : currentDate.getTime();
  let startDateTimestamp = startDateField
    ? new Date(startDateField).getTime()
    : new Date().setMonth(currentDate.getMonth() - DEFAULT_LOOKBACK_MONTHS);
  if (!startDateField || !endDateField) {
    updateDatePicker(startDateTimestamp, endDateTimestamp);
  }
  return [startDateTimestamp, endDateTimestamp];
};

const getAndRenderAnalytics = async () => {
  const [
    startDateTimestamp,
    endDateTimestamp,
  ] = getDateIntervalAndUpdateDatePicker();
  const requestUrl = `${baseUrl}/${API_PREFIX}${pathName}/?start_date=${startDateTimestamp}&end_date=${endDateTimestamp}`;
  const responseData = await (await fetch(requestUrl)).json();
  const root = document.getElementById("content");
  root.innerHTML = "";

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
    const datePickerContainer = document.getElementById(
      "date-picker-container"
    );
    datePickerContainer.style.display = "block";
    userJsonFile = responseData["user_json_file"];
    const pageHtml = composeStatisticsFromSingleUserJson(userJsonFile);
    root.insertAdjacentHTML("afterbegin", pageHtml);
    renderChartsFromSingleUserJson(userJsonFile);
  }
};

const addDateFilterEventListener = () => {
  const datePickerButton = document.getElementById("submit-date-btn");
  if (datePickerButton) {
    datePickerButton.addEventListener("click", () => {
      getAndRenderAnalytics();
    });
  }
};

window.onload = async () => {
  await getAndRenderAnalytics();
  addDateFilterEventListener();
};
