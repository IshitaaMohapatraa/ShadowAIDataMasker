# Shadow AI Sanitizer (Core Engine)

Lightweight, zero-trust Python privacy engine designed to intercept and sanitize sensitive data (API keys, PII, credentials) before transmission to external LLM providers.

> **Why This Matters:** When employees paste code or text into external AI tools (like ChatGPT), sensitive company data (passwords, credit card numbers, personal emails) can easily leak. This tool acts as an automatic filter that strips out sensitive credentials in real time before the data leaves your network.

## Features
* **Regex Rule Engine:** Detects OpenAI/AWS API keys, emails, credit cards, and phone numbers via compiled regex rules.
* **Surgical Redaction:** Replaces sensitive values with designated, traceable placeholders while maintaining context.
* **Audit Logging:** Generates structured JSON output detailing redaction metadata and string length metrics.
* **Automated Testing:** Validated with an automated `pytest` suite for high reliability.

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

### 3. Usage Example
Send a POST request to the /sanitize endpoint with prompt text containing sensitive information:
```bash 
curl.exe -X POST [http://127.0.0.1:5000/sanitize](http://127.0.0.1:5000/sanitize) \
  -H "Content-Type: application/json" \
  -d '{"prompt": "My key is sk-12345678901234567890123456789012 and email is dev@company.com"}'
  ```

### 4. Running Unit Tests
Execute the automated test suite using pytest:
```bash
pytest
```