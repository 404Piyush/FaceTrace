# Face -> Web Search -> Blockchain Verification (HH Goa 2026 Task 3)

Public-figure demo: upload a face scan, find a genuinely matching public image via
SerpAPI Google Lens, re-rank locally with DeepFace (OpenCV fallback if TF not installed),
anchor a SHA256 fingerprint in a hash-chained local ledger (chain.json), re-verify
(incl. tamper FAIL demo).

## Run
```
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # put SERPAPI_KEY=... (free 100/mo, no card)
streamlit run app.py
```
Warmup (optional, downloads DeepFace weights once with WiFi — skip if using fallback):
```
pip install deepface tf-keras
python -c "from deepface import DeepFace; DeepFace.represent(img_path='app.py',model_name='Facenet512',detector_backend='opencv',enforce_detection=False)"
```
Without DeepFace, `face_id.py` auto-uses an OpenCV histogram fallback so the demo runs.
CLI search:
```
python search.py --url https://files.catbox.moe/XXXXXX.jpg
```

## Flow (60s recording)
1. Upload face -> paste catbox URL -> Search -> side-by-side match + score + clickable post link + SerpAPI JSON.
2. Anchor -> tx_hash + block (instant, offline-safe).
3. Re-verify -> MATCH; edit snippet -> FAIL (tamper detected).

## Blockchain
Simulated hash-chained ledger (`blockchain.py`, stdlib only, `chain.json`): each block =
`SHA256(index|timestamp|fingerprint|prev_hash)`. Fingerprint = SHA256 of canonical JSON
`{post_url, image_sha256, text, retrieved_at}`. Verify checks stored fingerprint +
recomputes block hash + validates full chain. Task allows a local/simulated chain;
web3/EVM install failed on this machine (no C++ toolchain for safe-pysha3), so this
zero-dependency ledger keeps the demo offline-safe. Upgrade path: swap `anchor/verify`
for web3.py + eth-tester without changing `app.py`.

## Limitations
- Lens returns public indexed images only, not private socials; weak on unknown faces.
- SerpAPI free tier 100/mo.
- DeepFace CPU threshold-tuned, not production ID (OpenCV fallback auto-used if TF missing).
- Local simulated chain (single-node, not mainnet); EVM upgrade path documented.
- Public-figure / consenting-face demo only, not stranger tracking.
