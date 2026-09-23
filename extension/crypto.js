// Local AES-256-GCM Encryption Helper using Web Crypto API

let sessionKey = null;

export async function getOrCreateKey() {
  if (sessionKey) return sessionKey;
  
  sessionKey = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    false, // Non-extractable for memory protection
    ["encrypt", "decrypt"]
  );
  return sessionKey;
}

export async function encryptValue(plaintext) {
  const key = await getOrCreateKey();
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encoded = new TextEncoder().encode(plaintext);

  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    key,
    encoded
  );

  return {
    ciphertext: Array.from(new Uint8Array(ciphertext)),
    iv: Array.from(iv)
  };
}

export async function decryptValue(encryptedData) {
  const key = await getOrCreateKey();
  const iv = new Uint8Array(encryptedData.iv);
  const ciphertext = new Uint8Array(encryptedData.ciphertext);

  const decrypted = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: iv },
    key,
    ciphertext
  );

  return new TextDecoder().decode(decrypted);
}