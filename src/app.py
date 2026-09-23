import time
from flask import Flask, request, jsonify
from src.sanitizer import TextSanitizer

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


@app.route("/vault", methods=["GET"])
def get_vault():
  cleanup_stale_vault_entries()
  # Return simplified dictionary for response un-masking
  active_vault = {k: v["value"] for k, v in VAULT_STORE.items()}
  return jsonify({"vault": active_vault}), 200