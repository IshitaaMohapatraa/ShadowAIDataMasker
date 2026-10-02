console.log("[Shadow AI] Universal multi-engine content script loaded.");

// --- STATE CACHE FOR SYNCHRONOUS CHECK ---
let isMaskingEnabled = true;
chrome.storage.local.get(["maskingEnabled"], (res) => {
  if (res.maskingEnabled !== undefined) isMaskingEnabled = res.maskingEnabled;
});
chrome.storage.onChanged.addListener((changes) => {
  if (changes.maskingEnabled) {
    isMaskingEnabled = changes.maskingEnabled.newValue;
  }
});

// --- HEURISTIC INPUT FINDER ---
function getActiveInput() {
  const active = document.activeElement;

  if (
    active &&
    (active.tagName === "TEXTAREA" ||
      active.tagName === "INPUT" ||
      active.getAttribute("contenteditable") === "true" ||
      active.role === "textbox")
  ) {
    return active;
  }

  const selectors = [
    '#prompt-textarea',
    'div[contenteditable="true"][aria-label*="Claude"]',
    'div[contenteditable="true"][aria-label*="Gemini"]',
    'div[contenteditable="true"]',
    'textarea[placeholder*="Ask"]',
    'textarea[placeholder*="Anything"]',
    'textarea'
  ];

  for (const s of selectors) {
    const el = document.querySelector(s);
    if (el && el.offsetWidth > 0 && el.offsetHeight > 0) return el;
  }

  return null;
}

// --- UNIVERSAL TEXT INJECTOR ---
function injectSanitizedText(inputEl, text) {
  inputEl.focus();

  const isContentEditable =
    inputEl.getAttribute("contenteditable") === "true" ||
    inputEl.tagName !== "TEXTAREA";

  if (isContentEditable) {
    document.execCommand("selectAll", false, null);
    const inserted = document.execCommand("insertText", false, text);

    if (!inserted) {
      inputEl.textContent = text;
    }
  } else {
    const nativeSetter =
      Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set ||
      Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;

    if (nativeSetter) {
      nativeSetter.call(inputEl, text);
    } else {
      inputEl.value = text;
    }
  }

  inputEl.dispatchEvent(new Event("input", { bubbles: true, composed: true }));
  inputEl.dispatchEvent(new Event("change", { bubbles: true, composed: true }));
}

// --- UNIVERSAL SUBMIT TRIGGER ---
function triggerSubmission(inputEl) {
  const container = inputEl
    ? inputEl.closest("form, fieldset, main, div[class*='input'], div[class*='prompt']") || document
    : document;

  const selectors = [
    'button[aria-label*="Submit"]',
    'button[aria-label*="Send"]',
    'button[aria-label*="Search"]',
    'button[data-testid*="send"]',
    'button[data-testid*="submit"]',
    'button[type="submit"]',
    'button.bg-super'
  ];

  for (const selector of selectors) {
    const btns = Array.from(container.querySelectorAll(selector));
    const target = btns.find((b) => b.offsetWidth > 0 && b.offsetHeight > 0 && !b.disabled);
    if (target) {
      target.click();
      return true;
    }
  }

  const svgButtons = Array.from(container.querySelectorAll("button")).filter(
    (btn) => btn.querySelector("svg") && !btn.disabled && btn.offsetWidth > 0
  );

  if (svgButtons.length > 0) {
    svgButtons[svgButtons.length - 1].click();
    return true;
  }

  return false;
}

// --- KEYDOWN INTERCEPTOR ---
document.addEventListener(
  "keydown",
  (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      if (!isMaskingEnabled) return;

      const inputEl = getActiveInput();
      if (!inputEl) return;

      const rawText = (inputEl.value !== undefined ? inputEl.value : inputEl.innerText) || "";
      if (!rawText.trim()) return;

      // Skip if already sanitized
      if (rawText.includes("[REDACTED_")) return;

      // Immediately block browser submission before async gap
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();

      if (!chrome.runtime?.id) return;

      chrome.runtime.sendMessage(
        { action: "sanitize_prompt", prompt: rawText },
        (response) => {
          if (chrome.runtime.lastError || !response || !response.success) {
            console.warn("[Shadow AI] Masking request failed.");
            return;
          }

          const cleanPrompt = response.data.sanitized_prompt;

          injectSanitizedText(inputEl, cleanPrompt);

          setTimeout(() => {
            const submitted = triggerSubmission(inputEl);

            if (!submitted) {
              const form = inputEl.closest("form");
              if (form) {
                form.requestSubmit ? form.requestSubmit() : form.submit();
              }
            }
          }, 120);
        }
      );
    }
  },
  true // Capture phase
);

// --- IMAGE INTERCEPTION & OCR REDACTION ---
// --- UNIVERSAL IMAGE INTERCEPTION & OCR REDACTION ---
document.addEventListener('paste', handleImageInterception, true);
document.addEventListener('drop', handleImageInterception, true);

async function handleImageInterception(event) {
    if (!isMaskingEnabled) return;
    
    const items = event.clipboardData?.items || event.dataTransfer?.items;
    if (!items) return;

    for (let item of items) {
        if (item.type.startsWith('image/')) {
            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();

            const file = item.getAsFile();
            await uploadAndSwapImage(file, event.target);
            break;
        }
    }
}

async function uploadAndSwapImage(imageFile, targetElement) {
    try {
        console.log("[Shadow AI] Intercepting multi-modal image payload...");

        const reader = new FileReader();
        reader.readAsDataURL(imageFile);
        
        reader.onloadend = async () => {
            const imageDataUrl = reader.result;

            chrome.runtime.sendMessage(
                { action: "sanitize_image", imageDataUrl: imageDataUrl },
                async (response) => {
                    if (chrome.runtime.lastError || !response || !response.success) {
                        console.error("[Shadow AI] Image Redaction Error:", response?.error || chrome.runtime.lastError);
                        alert("Shadow AI Warning: Could not process image redaction. Upload halted for safety.");
                        return;
                    }

                    const res = await fetch(response.sanitizedDataUrl);
                    const sanitizedBlob = await res.blob();
                    const sanitizedFile = new File([sanitizedBlob], "sanitized_upload.png", { type: "image/png" });

                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(sanitizedFile);

                    // Strategy 1: Search broadly for file inputs across ChatGPT, Claude, and Gemini
                    let fileInput = document.querySelector('input[type="file"]') || 
                                    document.querySelector('form input[type="file"]') ||
                                    document.querySelector('input[accept*="image"]');

                    if (!fileInput) {
                        const allInputs = document.querySelectorAll('input');
                        for (let inp of allInputs) {
                            if (inp.type === 'file') {
                                fileInput = inp;
                                break;
                            }
                        }
                    }

                    if (fileInput) {
                        fileInput.files = dataTransfer.files;
                        fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                        fileInput.dispatchEvent(new Event('input', { bubbles: true }));
                        console.log("[Shadow AI] Scrubbed image successfully injected into file input!");
                    } else {
                        // Strategy 2: Gemini Clipboard Paste Fallback
                        console.log("[Shadow AI] File input missing. Simulating paste event on Gemini target...");
                        const editableArea = document.querySelector('rich-textarea') || 
                                             document.querySelector('div[contenteditable="true"]') || 
                                             targetElement;
                        
                        if (editableArea) {
                            editableArea.focus();
                            const pasteEvent = new ClipboardEvent('paste', {
                                bubbles: true,
                                cancelable: true,
                                clipboardData: dataTransfer
                            });
                            editableArea.dispatchEvent(pasteEvent);
                            console.log("[Shadow AI] Scrubbed image pasted into Gemini via clipboard event!");
                        } else {
                            alert("Shadow AI Warning: Could not locate upload target on Gemini.");
                        }
                    }
                }
            );
        };
    } catch (error) {
        console.error("[Shadow AI] Image Preparation Error:", error);
        alert("Shadow AI Warning: Could not process image. Upload halted for safety.");
    }
}

// --- UN-MASKING VAULT OBSERVER ---
function unmaskDOM() {
  if (!chrome.runtime?.id) return;

  chrome.runtime.sendMessage({ action: "get_vault" }, (response) => {
    if (chrome.runtime.lastError || !response || !response.vault) return;

    const vault = response.vault;
    const placeholders = Object.keys(vault);
    if (placeholders.length === 0) return;

    const targetNodes = document.querySelectorAll("p, code, pre, span, li, div");

    targetNodes.forEach((node) => {
      if (node.children.length === 0 && node.textContent.includes("[REDACTED_")) {
        let updatedText = node.textContent;
        placeholders.forEach((p) => {
          if (updatedText.includes(p)) {
            updatedText = updatedText.replaceAll(p, vault[p]);
          }
        });

        if (updatedText !== node.textContent) {
          node.textContent = updatedText;
          node.style.backgroundColor = "rgba(34, 197, 94, 0.15)";
          node.style.borderBottom = "1px dotted #22c55e";
        }
      }
    });
  });
}

let unmaskTimeout = null;
const observer = new MutationObserver(() => {
  if (unmaskTimeout) clearTimeout(unmaskTimeout);
  unmaskTimeout = setTimeout(() => unmaskDOM(), 300);
});

observer.observe(document.body, { childList: true, subtree: true });