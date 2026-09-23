# Shadow AI Sanitizer (Core Engine)

Lightweight, zero-trust Python privacy engine designed to intercept and sanitize sensitive data (API keys, PII, credentials) before transmission to external LLM providers.

> **Why This Matters:** When employees paste code or text into external AI tools (like ChatGPT), sensitive company data (passwords, credit card numbers, personal emails) can easily leak. This tool acts as an automatic filter that strips out sensitive credentials in real time before the data leaves your network.

## Features
* **Zero-Trust Client-Side Redaction:** Sanitizes prompt inputs locally before they ever hit external LLM vendor servers.
* **Dual-Layer Detection Engine:**
  * **Deterministic Rules:** High-precision regex pattern matching for cloud keys (AWS, OpenAI, GitHub, Google), JWT tokens, financial data (PAN, Credit Cards), and regional PII (Aadhaar, Emails).
  * **Heuristic Engine:** Shannon Entropy calculator scanning for unstructured, high-entropy raw secret keys.
* **Salted Cryptographic Tokens:** Generates dynamic, salted SHA-256 placeholder hashes (`[REDACTED_TYPE_HASH]`) to prevent collision, spoofing, and rainbow table lookups.
* **Seamless Response Un-Masking:** A DOM MutationObserver intercepts streaming responses and restores raw values locally with visual highlight indicators.
* **Multi-Engine Hybrid Injection:** Native prototype setter and DOM injection pipeline designed to support ChatGPT, Claude, Gemini, and DeepSeek.
* **Control Dashboard:** Chrome extension popup equipped with live session telemetry and a global ON/OFF protection toggle.

## System Architecture
```
Shadow AI Data Masker uses a hybrid client-side interception model combined with a lightweight local REST API to ensure zero-trust data sanitization before prompts leave the client's device.
+-----------------------------------------------------------------------------------+
|                                  BROWSER CLIENT                                   |
|                                                                                   |
|  +--------------------+    Enter Key Intercept    +----------------------------+  |
|  | Web LLM UI         | ------------------------> | content.js                 |  |
|  | (ChatGPT / Claude  |                           | (DOM Event Capture &       |  |
|  |  Gemini / DeepSeek)| <------------------------ |  Native Input Injector)    |  |
|  +--------------------+     Injected Redaction    +----------------------------+  |
|            ^                                                    |                 |
|            | Un-Masked DOM Text                                 | JSON Payload    |
|            |                                                    v                 |
|  +--------------------+                           +----------------------------+  |
|  | MutationObserver   | <------------------------ | background.js              |  |
|  | Response Unmasker  |    Local Session Vault    | (MV3 Service Worker)       |  |
|  +--------------------+                           +----------------------------+  |
+-----------------------------------------------------------------|-----------------+
|
HTTP POST  |  /sanitize
v
+-----------------------------------------------------------------------------------+
|                                 LOCAL FLASK ENGINE                                |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | TextSanitizer (src/sanitizer.py)                                           |  |
|  |  |-- Deterministic Pattern Engine (AWS, OpenAI, PII, PAN, Aadhaar Regex)   |  |
|  |  |-- Heuristic Entropy Engine (Shannon Entropy Scanner)                     |  |
|  |  '-- Salted Token Generator (HMAC / Cryptographic SHA-256 Hash Placeholders) |  |
|  +-----------------------------------------------------------------------------+  |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  | Ephemeral In-Memory Vault (src/app.py)                                       |  |
|  |  '-- Stores Mapping Pair: [REDACTED_TYPE_HASH] <-> Raw Secret (15-Min TTL)    |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Data Flow Lifecycle
1. **Interception:** `content.js` intercepts the DOM `keydown` event on input editors (supporting rich `contenteditable` and standard `textarea` elements) across supported LLM platforms.
2. **Local Sanitization:** The prompt payload is routed to the local Flask backend (`http://127.0.0.1:5000/sanitize`). The engine evaluates both deterministic regex rules and Shannon entropy scores to replace sensitive tokens with cryptographically salted placeholders (`[REDACTED_TYPE_HASH]`).
3. **Vault Mapping:** Raw values are stored in an ephemeral, in-memory vault with a 15-minute Time-To-Live (TTL) auto-purge cycle.
4. **Input Replacement & Dispatch:** `content.js` injects the sanitized prompt directly into the LLM editor using native prototype setters and dispatches `input` events before triggering the submission button.
5. **Response Un-Masking:** As the LLM streams its response, a background `MutationObserver` scans target text nodes against active vault keys, restoring original sensitive values exclusively on the user's local screen with visual highlight indicators.

## Getting Started

### 1. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/IshitaaMohapatraa/Shadow-AI-Data-Masker.git
cd "Shadow AI Data Masker"
pip install -r requirements.txt
```
### 2. Run the API Server
Start the Flask backend application locally:
```bash
python src/app.py
```
The server will initialize at http://127.0.0.1:5000

### 3. Load the Chrome Extension
1) Open Google Chrome and navigate to chrome://extensions/.
2) Enable Developer mode using the toggle switch in the top-right corner.
3) Click Load unpacked and select the extension/ directory from this project.

### 4. API Usage Example
Send a POST request to the /sanitize endpoint with prompt text containing sensitive information:
```bash 
curl.exe -X POST [http://127.0.0.1:5000/sanitize](http://127.0.0.1:5000/sanitize) \
  -H "Content-Type: application/json" \
  -d '{"prompt": "My key is sk-12345678901234567890123456789012 and email is dev@company.com"}'
  ```

### 5. Running Unit Tests
Execute the automated test suite using pytest:
```bash
pytest
```

## Known Limitations:
* **Perplexity AI:** Pending rich-text Lexical editor state synchronization support.