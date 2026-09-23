// Shadow AI Service Worker - Session Vault Handler

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "sanitize_prompt") {
    fetch("http://127.0.0.1:5000/sanitize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt: request.prompt })
    })
      .then((res) => res.json())
      .then(async (data) => {
        // Store vault mapping into volatile chrome.storage.session
        if (data.audit_log && data.audit_log.length > 0) {
          const sessionVault = (await chrome.storage.session.get("vault")).vault || {};
          
          data.audit_log.forEach((item) => {
            // Map placeholder back to original value for response un-masking
            sessionVault[item.placeholder] = item.original_value;
          });

          await chrome.storage.session.set({ vault: sessionVault });
          
          // Increment total redacted counter for UI stats
          const currentCount = (await chrome.storage.session.get("redact_count")).redact_count || 0;
          await chrome.storage.session.set({ redact_count: currentCount + data.audit_log.length });
        }

        sendResponse({ success: true, data: data });
      })
      .catch((err) => sendResponse({ success: false, error: err.toString() }));

    return true; // Keep channel open for async response
  }

  if (request.action === "get_vault") {
    chrome.storage.session.get("vault").then((res) => {
      sendResponse({ vault: res.vault || {} });
    });
    return true;
  }

  if (request.action === "get_stats") {
    chrome.storage.session.get(["redact_count", "vault"]).then((res) => {
      sendResponse({ 
        count: res.redact_count || 0,
        vaultSize: Object.keys(res.vault || {}).length 
      });
    });
    return true;
  }
});