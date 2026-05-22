(function () {
  const stateSelect = document.getElementById("state-select");
  const citySelect = document.getElementById("city-select");
  const cityInput = document.getElementById("city-input");
  const suggestionBox = document.getElementById("city-suggestions");
  const locationFeedback = document.getElementById("location-feedback");
  const severitySelect = document.getElementById("severity-select");
  const emergencyInput = document.getElementById("emergency-input");
  const selectionPreview = document.getElementById("selection-preview");
  const submitButton = document.getElementById("submit-button");
  const triageForm = document.querySelector(".triage-form");
  const emergencyCards = Array.from(document.querySelectorAll(".select-card"));

  if (!stateSelect || !citySelect || !cityInput || !emergencyInput || !triageForm) {
    return;
  }

  const severityLabels = {
    "1": "low",
    "2": "moderate",
    "3": "serious",
    "4": "critical",
    "5": "life-threatening"
  };

  let suggestionItems = [];
  let activeSuggestionIndex = -1;
  let cityRequestToken = 0;

  const titleCase = (value) =>
    String(value || "")
      .trim()
      .replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());

  const populateSelect = (select, placeholder, values) => {
    select.innerHTML = "";

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;
    select.appendChild(placeholderOption);

    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = titleCase(value);
      select.appendChild(option);
    });
  };

  const setLocationFeedback = (message) => {
    if (locationFeedback) {
      locationFeedback.textContent = message;
    }
  };

  const updateSelectionPreview = () => {
    if (!selectionPreview) {
      return;
    }

    const emergency = emergencyInput.value || "General";
    const severityValue = severitySelect ? severitySelect.value : "2";
    const severity = severityLabels[severityValue] || "moderate";
    const city = cityInput.value.trim();
    const state = stateSelect.value.trim();

    let locationText = "for the selected location";
    if (city && state) {
      locationText = `for ${titleCase(city)}, ${titleCase(state)}`;
    } else if (city) {
      locationText = `for ${titleCase(city)}`;
    } else if (state) {
      locationText = `for hospitals in ${titleCase(state)}`;
    }

    selectionPreview.textContent = `Ready to rank a ${severity} ${emergency.toLowerCase()} case ${locationText}.`;
  };

  const clearSuggestions = () => {
    suggestionItems = [];
    activeSuggestionIndex = -1;
    suggestionBox.innerHTML = "";
    suggestionBox.classList.remove("has-results");
  };

  const applyCityValue = (value) => {
    const normalized = titleCase(value);
    cityInput.value = normalized;

    const matchingOption = Array.from(citySelect.options).find(
      (option) => option.value.toLowerCase() === value.toLowerCase()
    );

    if (matchingOption) {
      citySelect.value = matchingOption.value;
      setLocationFeedback(`City locked to ${matchingOption.textContent}. You can still type a custom city if needed.`);
    } else {
      citySelect.value = "";
      setLocationFeedback(`Using manual city input: ${normalized}.`);
    }

    clearSuggestions();
    updateSelectionPreview();
  };

  const highlightSuggestion = (index) => {
    suggestionItems.forEach((item, itemIndex) => {
      item.classList.toggle("is-active", itemIndex === index);
    });
  };

  const renderSuggestions = (cities) => {
    clearSuggestions();

    if (!cities.length) {
      return;
    }

    const fragment = document.createDocumentFragment();
    suggestionItems = cities.map((city) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "suggestion-item";
      button.textContent = titleCase(city);
      button.addEventListener("click", () => applyCityValue(city));
      fragment.appendChild(button);
      return button;
    });

    suggestionBox.appendChild(fragment);
    suggestionBox.classList.add("has-results");
  };

  const fetchJson = async (url) => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  };

  const loadStates = async () => {
    try {
      const states = await fetchJson("/states");
      populateSelect(stateSelect, "Select state", states);
      setLocationFeedback("Select a state to narrow the city list, or start typing directly.");
    } catch (error) {
      populateSelect(stateSelect, "State unavailable", []);
      setLocationFeedback("State lookup is unavailable right now. You can still type the city manually.");
      console.error(error);
    }
  };

  const loadCitiesForState = async (state) => {
    if (!state) {
      populateSelect(citySelect, "Select state first", []);
      setLocationFeedback("Select a state to narrow the city list, or start typing directly.");
      updateSelectionPreview();
      return;
    }

    try {
      const cities = await fetchJson(`/cities_by_state?state=${encodeURIComponent(state)}`);
      populateSelect(citySelect, cities.length ? "Select city" : "No listed cities", cities);
      setLocationFeedback(
        cities.length
          ? `${cities.length} cities loaded for ${titleCase(state)}.`
          : `No listed cities were found for ${titleCase(state)}. You can still enter the city manually.`
      );
    } catch (error) {
      populateSelect(citySelect, "City lookup unavailable", []);
      setLocationFeedback("City lookup is unavailable right now. Please type the city manually.");
      console.error(error);
    }

    updateSelectionPreview();
  };

  const loadCitySuggestions = async (query) => {
    if (query.length < 2) {
      clearSuggestions();
      return;
    }

    cityRequestToken += 1;
    const requestToken = cityRequestToken;

    try {
      const matches = await fetchJson(`/cities?q=${encodeURIComponent(query)}`);
      if (requestToken !== cityRequestToken) {
        return;
      }
      renderSuggestions(matches);
    } catch (error) {
      clearSuggestions();
      console.error(error);
    }
  };

  emergencyCards.forEach((card) => {
    card.addEventListener("click", () => {
      emergencyCards.forEach((otherCard) => {
        otherCard.classList.remove("active");
        otherCard.setAttribute("aria-pressed", "false");
      });

      card.classList.add("active");
      card.setAttribute("aria-pressed", "true");
      emergencyInput.value = card.dataset.value || "General";
      updateSelectionPreview();
    });
  });

  stateSelect.addEventListener("change", (event) => {
    loadCitiesForState(event.target.value);
  });

  citySelect.addEventListener("change", (event) => {
    const value = event.target.value;
    if (!value) {
      return;
    }
    applyCityValue(value);
  });

  cityInput.addEventListener("input", (event) => {
    const value = event.target.value.trim();
    updateSelectionPreview();

    if (!value) {
      clearSuggestions();
      setLocationFeedback(
        stateSelect.value
          ? `State locked to ${titleCase(stateSelect.value)}. Select a city or continue typing manually.`
          : "Select a state to narrow the city list, or start typing directly."
      );
      return;
    }

    setLocationFeedback(`Searching the dataset for matches to "${titleCase(value)}"...`);
    loadCitySuggestions(value);
  });

  cityInput.addEventListener("keydown", (event) => {
    if (!suggestionItems.length) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      activeSuggestionIndex = (activeSuggestionIndex + 1) % suggestionItems.length;
      highlightSuggestion(activeSuggestionIndex);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      activeSuggestionIndex =
        activeSuggestionIndex <= 0 ? suggestionItems.length - 1 : activeSuggestionIndex - 1;
      highlightSuggestion(activeSuggestionIndex);
      return;
    }

    if (event.key === "Enter" && activeSuggestionIndex >= 0) {
      event.preventDefault();
      suggestionItems[activeSuggestionIndex].click();
      return;
    }

    if (event.key === "Escape") {
      clearSuggestions();
    }
  });

  severitySelect.addEventListener("change", updateSelectionPreview);

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".autocomplete")) {
      clearSuggestions();
    }
  });

  triageForm.addEventListener("submit", () => {
    if (!submitButton) {
      return;
    }

    submitButton.classList.add("is-loading");
    submitButton.disabled = true;
    submitButton.textContent = "Ranking hospitals...";
  });

  loadStates();
  updateSelectionPreview();
})();
