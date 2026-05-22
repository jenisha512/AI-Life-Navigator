(function () {
  const hospitals = Array.isArray(window.hospitalResultsData) ? window.hospitalResultsData : [];
  const toast = document.getElementById("page-toast");
  const mapElement = document.getElementById("map");
  const chartCanvas = document.getElementById("icuChart");
  const copyButtons = document.querySelectorAll(".copy-emergency");
  const hospitalCards = document.querySelectorAll(".hospital-card");
  const copySummaryButton = document.getElementById("copy-summary");
  const printBriefingButton = document.getElementById("print-briefing");
  const chatbotContext = document.getElementById("chatbot-container")?.dataset || {};

  if (!hospitals.length) {
    return;
  }

  let toastTimer = null;

  const toNumber = (value) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  };

  const validHospitals = hospitals.filter((hospital) => {
    return toNumber(hospital.latitude) !== null && toNumber(hospital.longitude) !== null;
  });

  const getMapCenter = (items) => {
    if (!items.length) {
      return null;
    }

    const totals = items.reduce(
      (accumulator, hospital) => {
        accumulator.lat += Number(hospital.latitude);
        accumulator.lon += Number(hospital.longitude);
        return accumulator;
      },
      { lat: 0, lon: 0 }
    );

    return {
      lat: totals.lat / items.length,
      lon: totals.lon / items.length
    };
  };

  const haversineDistance = (lat1, lon1, lat2, lon2) => {
    const toRadians = (degrees) => (degrees * Math.PI) / 180;
    const earthRadiusKm = 6371;
    const deltaLat = toRadians(lat2 - lat1);
    const deltaLon = toRadians(lon2 - lon1);
    const a =
      Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
      Math.cos(toRadians(lat1)) *
        Math.cos(toRadians(lat2)) *
        Math.sin(deltaLon / 2) *
        Math.sin(deltaLon / 2);

    return earthRadiusKm * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  };

  const showToast = (message, tone) => {
    if (!toast) {
      return;
    }

    toast.textContent = message;
    toast.classList.remove("is-error", "is-success");
    toast.classList.add("visible", tone === "error" ? "is-error" : "is-success");

    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => {
      toast.classList.remove("visible", "is-error", "is-success");
    }, 2400);
  };

  const updateDistanceLabels = () => {
    const center = getMapCenter(validHospitals);

    hospitalCards.forEach((card) => {
      const distanceElement = card.querySelector(".distance-text");
      if (!distanceElement) {
        return;
      }

      const lat = toNumber(card.dataset.lat);
      const lon = toNumber(card.dataset.lon);

      if (!center || lat === null || lon === null) {
        distanceElement.textContent = "Unavailable";
        return;
      }

      const distance = haversineDistance(center.lat, center.lon, lat, lon);
      distanceElement.textContent = distance < 1 ? "Under 1 km" : `${distance.toFixed(1)} km`;
    });
  };

  const initMap = () => {
    if (!mapElement || typeof L === "undefined" || !validHospitals.length) {
      if (mapElement && !validHospitals.length) {
        mapElement.innerHTML = "<p class=\"field-help\">Location coordinates are unavailable for this result set.</p>";
      }
      return;
    }

    const center = getMapCenter(validHospitals);
    const map = L.map(mapElement, { scrollWheelZoom: false, zoomControl: true });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    const bounds = [];

    validHospitals.forEach((hospital, index) => {
      const lat = Number(hospital.latitude);
      const lon = Number(hospital.longitude);
      const marker = L.circleMarker([lat, lon], {
        radius: index === 0 ? 10 : 8,
        color: index === 0 ? "#0b6d69" : "#103b5a",
        weight: 2,
        fillColor: index === 0 ? "#0f8e8a" : "#ffffff",
        fillOpacity: 0.95
      });

      marker
        .addTo(map)
        .bindPopup(
          `<strong>${hospital.hospital_name}</strong><br>` +
            `Rank ${index + 1}<br>` +
            `Score: ${hospital.score}<br>` +
            `ICU load: ${hospital.current_icu_load_percent}%`
        );

      bounds.push([lat, lon]);
    });

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [40, 40] });
    } else if (center) {
      map.setView([center.lat, center.lon], 11);
    }
  };

  const initChart = () => {
    if (!chartCanvas || typeof Chart === "undefined") {
      return;
    }

    const labels = hospitals.map((hospital, index) => {
      const shortName =
        hospital.hospital_name.length > 22
          ? `${hospital.hospital_name.slice(0, 22)}...`
          : hospital.hospital_name;
      return `#${index + 1} ${shortName}`;
    });

    new Chart(chartCanvas, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Ranking score",
            data: hospitals.map((hospital) => hospital.score),
            backgroundColor: "rgba(15, 142, 138, 0.75)",
            borderRadius: 10,
            maxBarThickness: 36
          },
          {
            type: "line",
            label: "ICU load %",
            data: hospitals.map((hospital) => hospital.current_icu_load_percent),
            borderColor: "#c34f5f",
            backgroundColor: "rgba(195, 79, 95, 0.18)",
            yAxisID: "loadAxis",
            tension: 0.32,
            fill: false,
            pointRadius: 4,
            pointHoverRadius: 5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false
        },
        plugins: {
          legend: {
            position: "bottom"
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Ranking score"
            },
            grid: {
              color: "rgba(16, 33, 57, 0.08)"
            }
          },
          loadAxis: {
            beginAtZero: true,
            max: 100,
            position: "right",
            title: {
              display: true,
              text: "ICU load %"
            },
            grid: {
              drawOnChartArea: false
            }
          }
        }
      }
    });
  };

  const fallbackCopy = (text) => {
    const input = document.createElement("input");
    input.value = text;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
  };

  const copyEmergencyNumber = async (number) => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(number);
      } else {
        fallbackCopy(number);
      }
      showToast(`Emergency number ${number} copied.`, "success");
    } catch (error) {
      showToast("Could not copy the emergency number on this device.", "error");
      console.error(error);
    }
  };

  const getDistanceText = (hospital) => {
    const center = getMapCenter(validHospitals);
    const lat = toNumber(hospital.latitude);
    const lon = toNumber(hospital.longitude);

    if (!center || lat === null || lon === null) {
      return "Distance estimate unavailable";
    }

    const distance = haversineDistance(center.lat, center.lon, lat, lon);
    return distance < 1 ? "Under 1 km from the selected area center" : `${distance.toFixed(1)} km from the selected area center`;
  };

  const copyText = async (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }

    fallbackCopy(text);
  };

  const buildReferralSummary = () => {
    const primary = hospitals[0];
    if (!primary) {
      return "";
    }

    return [
      "MedRoute AI referral briefing",
      `Hospital: ${primary.hospital_name}`,
      `Emergency: ${chatbotContext.emergency || "Selected case type"}`,
      `Severity: ${chatbotContext.severity || "Selected severity"}`,
      `City: ${chatbotContext.city || "Selected area"}`,
      `Care level: ${primary.hospital_level}`,
      `Ranking score: ${primary.score}`,
      `Confidence: ${primary.confidence_label}`,
      `ICU beds: ${primary.icu_beds}`,
      `ICU load: ${primary.current_icu_load_percent}%`,
      `Reason: ${primary.recommendation_reason}`,
      `Distance: ${getDistanceText(primary)}`
    ].join("\n");
  };

  copyButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const number = button.dataset.number || "112";
      copyEmergencyNumber(number);
    });
  });

  if (copySummaryButton) {
    copySummaryButton.addEventListener("click", async () => {
      try {
        await copyText(buildReferralSummary());
        showToast("Referral summary copied.", "success");
      } catch (error) {
        showToast("Could not copy the referral summary.", "error");
        console.error(error);
      }
    });
  }

  if (printBriefingButton) {
    printBriefingButton.addEventListener("click", () => {
      window.print();
    });
  }

  updateDistanceLabels();
  initMap();
  initChart();
})();
