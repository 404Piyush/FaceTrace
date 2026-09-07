# Face -> Web Search -> Blockchain Verification (HH Goa 2026 Task 3)

Public-figure demo: upload a face scan, find a genuinely matching public image via
SerpAPI Google Lens, re-rank locally with real face embeddings (YuNet detection +
ArcFace R50 cosine similarity), anchor a SHA256 fingerprint in a hash-chained local
ledger (chain.json), re-verify (incl. tamper FAIL demo).

## Run
```
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python download_model.py    # ArcFace R50 weights (~167MB, once)
python download_yunet.py    # YuNet detector (~230KB, once)
copy .env.example .env   # put SERPAPI_KEY=... (free 100/mo, no card)
streamlit run app.py
```
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
- ArcFace R50 embeddings (InsightFace buffalo_l weights), cosine threshold 0.45, CPU-only.
- Local simulated chain (single-node, not mainnet); EVM upgrade path documented.
- Public-figure / consenting-face demo only, not stranger tracking.
