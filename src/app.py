import time
import io
from flask import Flask, request, jsonify, send_file
from src.sanitizer import TextSanitizer
from src.image_sanitizer import ImageSanitizer

app = Flask(__name__)

# Vault store with timestamps: { placeholder: {"value": raw, "timestamp": time.time()} }
VAULT_STORE = {}
VAULT_TTL_SECONDS = 900  # 15 minutes

def cleanup_stale_vault_entries():
  """Purges entries older than the defined TTL."""
  now = time.time()
  stale_keys = [
      k
      for k, v in VAULT_STORE.items()
      if now - v["timestamp"] > VAULT_TTL_SECONDS
  ]
  for k in stale_keys:
    del VAULT_STORE[k]


@app.route("/sanitize", methods=["POST"])
def sanitize():
  cleanup_stale_vault_entries()
  data = request.get_json() or {}
  prompt = data.get("prompt", "")

  if not prompt:
    return jsonify({"error": "No prompt provided"}), 400

  sanitized_prompt, vault = TextSanitizer.sanitize(prompt)

  # Store values with creation timestamp
  now = time.time()
  for placeholder, raw_val in vault.items():
    VAULT_STORE[placeholder] = {"value": raw_val, "timestamp": now}

  return (
      jsonify({"sanitized_prompt": sanitized_prompt, "vault": vault}),
      200,
  )


@app.route("/sanitize-image", methods=["POST"])
def sanitize_image_endpoint():
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400
    
    file = request.files['image']
    image_bytes = file.read()

    try:
        sanitized_bytes = ImageSanitizer.sanitize_image(image_bytes)
        return send_file(
            io.BytesIO(sanitized_bytes),
            mimetype='image/png',
            as_attachment=True,
            download_name='sanitized_upload.png'
        )
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/vault", methods=["GET"])
def get_vault():
  cleanup_stale_vault_entries()
  # Return simplified dictionary for response un-masking
  active_vault = {k: v["value"] for k, v in VAULT_STORE.items()}
  return jsonify({"vault": active_vault}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes so the extension can talk to Flask