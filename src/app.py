from flask import Flask, jsonify, request
from src.sanitizer import TextSanitizer

app = Flask(__name__)
sanitizer = TextSanitizer()

@app.route("/sanitize", methods=["POST"])
def sanitize_prompt():
    data = request.get_json(silent=True)
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' key in JSON payload"}), 400

    raw_prompt = data["prompt"]
    clean_prompt, audit_log = sanitizer.sanitize(raw_prompt)

    return jsonify({
        "status": "success",
        "original_length": len(raw_prompt),
        "sanitized_prompt": clean_prompt,
        "redactions_count": len(audit_log),
        "audit_log": audit_log
    }), 200

if __name__ == "__main__":
    print("--- Shadow AI Sanitizer Engine Online ---")
    demo_input = "Hey LLM, my OpenAI key is sk-abc123456789012345678901234567890 and email is dev@company.com"
    clean_out, logs = sanitizer.sanitize(demo_input)
    print(f"Sample Input : {demo_input}")
    print(f"Sample Output: {clean_out}\n")
    app.run(port=5000, debug=True)