# Architecture — FaceTrace

## Pipeline

`input.jpg → search.py → face_id.py → blockchain.py → app.py`. Each stage is one
module with a narrow interface so any stage can be swapped without touching the others.

### Stage 1 — Web search (`search.py`)

`lens_search(public_url)` calls SerpAPI `engine=google_lens` with the query's public URL
(upload to catbox.moe/transfer.sh first — Lens cannot read local files). It keeps the
top-5 `visual_matches` as `{title, link, thumbnail}`, persists them to `candidates.json`,
and `download_candidates()` fetches thumbnails into `gallery/`. `search.py --url …` runs
the same path headless. `load_cached()` reads the committed JSON when live search fails.

Why top-5: enough for a ranked comparison, cheap on the 100/mo free tier, fast on CPU.

### Stage 2 — Face verification (`face_id.py`)

YuNet (`models/yunet.onnx`, OpenCV `FaceDetectorYN`) detects and crops the largest face
with 15% padding; ArcFace R50 (`models/w600k_r50.onnx`, InsightFace `buffalo_l` weights,
ONNX Runtime CPU) embeds the 112×112 aligned crop to a 512-D L2-normed vector.
`verify_pair()` returns cosine similarity; match iff `sim ≥ 0.45`. `find_best()` ranks
all downloaded candidates. Images with no detectable face return `verified=False`
instead of crashing the ranking.

Measured on the reference query (Sept 2026): near-duplicate 0.951, source re-find 0.941,
same-event thumbnails ~0.92, cross-photo IG/X shots 0.74–0.76. Ranking separates
near-duplicate > same-event > different-photo, which is exactly what the demo narrates.

### Stage 3 — Ledger (`blockchain.py`, stdlib only)

`fingerprint(record)` = SHA-256 over canonical JSON
`{post_url, image_sha256, text, retrieved_at}` (sorted keys, compact separators).
`anchor()` appends `{index, timestamp, fingerprint, prev_hash, block_hash}` to `chain.json`
with `block_hash = SHA256(index|timestamp|fingerprint|prev_hash)`.
`verify(fp, tx_hash)` checks the stored fingerprint *and* recomputes the block hash;
`verify_chain()` walks the full history. Tampered fields change the fingerprint, so
re-verification fails closed with `False`.

### UI (`app.py`)

Streamlit, three buttons sharing `st.session_state`: Search (Lens → download → rank →
side-by-side + score + post link + raw-JSON expander), Anchor (build record → fingerprint
→ anchor → tx/block display), Re-verify (recompute from the editable fields → MATCH/FAIL
+ fingerprint diff). No auth, no database, no website — the task requires none.

## Why not a public testnet tonight

Polygon Amoy via Alchemy was the backup plan (same `anchor()/verify()` seam, free faucet,
2–5s confirms). It was cut for deadline reliability: faucet + Wi-Fi become single points
of failure on camera, while the task explicitly allows a local/simulated chain "as long
as you can demonstrate re-verifying the data against the on-chain record" — which the
MATCH → tamper → FAIL sequence does. A `web3.py + eth-tester` local EVM was attempted
first and abandoned: `safe-pysha3` needs a C++ build chain this machine lacks. To go
public later, implement `anchor()/verify()` against an RPC endpoint and keep `app.py`
unchanged.

## Key files

| File | Role |
|------|------|
| `app.py` | Streamlit demo shell |
| `face_id.py` | detection + embedding + ranking |
| `search.py` | Lens client + downloader + CLI |
| `blockchain.py` | fingerprint + ledger + verification |
| `download_model.py` / `download_yunet.py` | one-time weight fetchers (weights gitignored) |
| `candidates.json` | cached live response, offline fallback |
