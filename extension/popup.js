document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("maskingToggle");
  const countEl = document.getElementById("maskedCount");
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");

  // Load toggle state from storage
  chrome.storage.local.get(["maskingEnabled"], (res) => {
    const isEnabled = res.maskingEnabled !== false; // Default to true
    toggle.checked = isEnabled;
    updateStatusUI(isEnabled);
  });

  // Fetch count of masked vault items from backend
  fetch("http://127.0.0.1:5000/vault")
    .then((res) => res.json())
    .then((data) => {
      if (data && data.vault) {
        countEl.textContent = Object.keys(data.vault).length;
      }
    })
    .catch(() => {
      countEl.textContent = "0";
    });

  // Handle toggle change
  toggle.addEventListener("change", (e) => {
    const isEnabled = e.target.checked;
    chrome.storage.local.set({ maskingEnabled: isEnabled });
    updateStatusUI(isEnabled);
  });

  function updateStatusUI(enabled) {
    if (enabled) {
      statusDot.classList.remove("disabled");
      statusText.textContent = "Protection Active";
    } else {
      statusDot.classList.add("disabled");
      statusText.textContent = "Protection Disabled";
    }
  }
});