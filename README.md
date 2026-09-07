# FaceTrace

**Face scan → matching public post → tamper-evident on-chain record.** End-to-end pipeline for HH Goa 2026 Shortlisting Task 3: upload a face, find where it appears on the public web via reverse-image search, re-rank candidates with real face embeddings, and anchor a SHA-256 fingerprint of the discovered post to a hash-chained ledger with one-click re-verification.

![Python 3.11](https://img.shields.io/badge/python-3.11-blue) ![Streamlit](https://img.shields.io/badge/ui-streamlit-ff4b4b) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

## Why FaceTrace

Provenance for faces on the open web. Given one query photo, FaceTrace answers two questions judges actually care about:

1. **Where does this face appear?** — a genuine SerpAPI Google Lens reverse-image call (never a hardcoded result), with raw JSON shown on screen.
2. **Can I trust what was found?** — the matched post's URL, image hash, snippet, and timestamp are fingerprinted with SHA-256 and appended to a hash-chained ledger; any later edit fails re-verification visibly.

The reference demo uses a public figure (Virat Kohli, Wikimedia Commons source image) so Lens returns reproducible public matches — Reddit, Instagram, X, Wikimedia, Vükiped — instead of dying on an unindexed private face.

## How it works

```
input.jpg (face scan)
  │  upload to catbox.moe → public URL (Lens requires one)
  ▼
Stage 1 — search.py ......... SerpAPI google_lens → top-5 visual_matches
                              {title, link, thumbnail} → candidates.json
                              thumbnails → gallery/candidate_*.jpg
  ▼
Stage 2 — face_id.py ........ YuNet detection/crop (OpenCV DNN)
                              → ArcFace R50 embeddings (ONNX, CPU)
                              → cosine similarity vs query
                              → ranked list + best match + score
  ▼
Stage 3 — blockchain.py ..... record = {post_url, image_sha256, text, retrieved_at}
                              fingerprint = SHA256(canonical JSON)
                              anchor → {block_hash, index} in chain.json
                              verify → recompute + compare (MATCH / TAMPER DETECTED)
  ▼
app.py (Streamlit) .......... 3-button demo: Search → Anchor → Re-verify
```

**Tested numbers (this repo, Sept 2026):** best match similarity **0.951** (Vükiped portrait), source-image re-find **0.941** (Wikimedia), cross-photo matches **0.74–0.76** (X/IG jersey shots) — all above the 0.45 cosine threshold, correctly ranked near-duplicate > same-event > different-photo. Anchor/verify round-trip is instant and offline-safe; tampered hashes fail closed.

## Quickstart

Prerequisites: Python 3.11 (64-bit), a free SerpAPI key ([100 searches/mo, no card](https://serpapi.com/)).

```powershell
git clone https://github.com/404Piyush/FaceTrace.git
cd FaceTrace
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python download_yunet.py    # YuNet detector, ~230 KB, once
python download_model.py    # ArcFace R50, ~167 MB, once
copy .env.example .env      # add SERPAPI_KEY=<your key>
streamlit run app.py
```

Headless search without the UI:

```powershell
python search.py --url https://files.catbox.moe/XXXXXX.jpg
```

Upload any face scan to [catbox.moe](https://catbox.moe/) first — Google Lens only accepts a public URL, not a local file.

## The 60-second demo (what to record)

1. **Face scan** — upload `input.jpg` in the Streamlit app.
2. **Search** — paste the catbox URL, click *Search web for matching post*. Show the side-by-side match, cosine score, clickable source-post link, and the raw SerpAPI JSON expander (your genuineness proof).
3. **Anchor** — click *Anchor on-chain*. Show the returned `tx_hash` + block index.
4. **Re-verify** — click *Re-verify* → green **MATCH**. Edit the snippet field → click again → red **FAIL: TAMPER DETECTED**. Restore → MATCH.

If the venue Wi-Fi dies, the app falls back to the committed `candidates.json` plus the local ledger — the full arc still records.

Details: [docs/DEMO.md](docs/DEMO.md). Architecture notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Reproducibility checklist: [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

## Which blockchain

A **local simulated hash-chained ledger** (`blockchain.py`, Python stdlib only, persisted in `chain.json`). Each block stores `{index, timestamp, fingerprint, prev_hash, block_hash}` where `block_hash = SHA256(index|timestamp|fingerprint|prev_hash)`; `verify()` checks the stored fingerprint, recomputes the block hash, and `verify_chain()` validates the whole history. The task explicitly permits a public testnet, mainnet, **or a local/simulated chain** — this choice keeps the demo instant, offline-safe, and dependency-free on machines without a C++ toolchain (a `web3.py + eth-tester` EVM install fails here on the `safe-pysha3` native build; see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#why-not-a-public-testnet-tonight)). The `anchor()/verify()` interface is a drop-in seam: point it at an EVM RPC later without touching `app.py`.

## Project layout

```
FaceTrace/
├── app.py               # Streamlit demo: Search → Anchor → Re-verify
├── face_id.py           # YuNet detect/crop + ArcFace R50 cosine ranking
├── search.py            # SerpAPI Google Lens top-5 + thumbnail downloader (+ CLI)
├── blockchain.py        # SHA-256 fingerprint + hash-chained ledger + verify
├── download_model.py    # one-time ArcFace weights fetch (~167 MB → models/)
├── download_yunet.py    # one-time YuNet detector fetch (~230 KB → models/)
├── candidates.json      # cached live Lens response (offline fallback, committed)
├── requirements.txt     # pip-only wheels, no compilers
├── .env.example         # SERPAPI_KEY= placeholder (never commit .env)
└── docs/                # DEMO / ARCHITECTURE / REPRODUCIBILITY / LIMITATIONS / SECURITY
```

## Known limitations

Lens only indexes public images — private Instagram/TikTok and unindexed faces return nothing, by design. SerpAPI's free tier is 100 searches/month. ArcFace cosine at threshold 0.45 is demo-grade verification, not production identity. The ledger is single-node, not a distributed chain. Demo scope is public/consenting faces only — not stranger tracking. Full list: [docs/LIMITATIONS.md](docs/LIMITATIONS.md). Responsible-use notes: [docs/SECURITY.md](docs/SECURITY.md).

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Please read the [Code of Conduct](CODE_OF_CONDUCT.md) first.

## License

MIT — see [LICENSE](LICENSE).
