/* ---------- random 32-byte hex string ---------------------------------- */
const r = (() => {
  const bytes = new Uint8Array(32);          // 256 bits of entropy
  crypto.getRandomValues(bytes);
  return [...bytes].map(b => b.toString(16).padStart(2, '0')).join('');
})();

/* ---------- SHA-256 → base64url helper --------------------------------- */
async function sha256Base64Url(str) {
  const data       = new TextEncoder().encode(str);
  const hashBuf    = await crypto.subtle.digest('SHA-256', data); // ArrayBuffer
  const hashBytes  = new Uint8Array(hashBuf);
  const b64        = btoa(String.fromCharCode(...hashBytes));

  // convert to base64url
  return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/* ---------- run --------------------------------------------------------- */
(async () => {
  const n = await sha256Base64Url(r);
  a = r === n ? "plain" : "s256";
  console.log('random hex :', r);
  console.log('SHA-256 b64url :', n);
})();
