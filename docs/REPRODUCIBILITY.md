# Reproducibility — FaceTrace

Everything below was run on Windows 11, Python 3.11.4 (64-bit), CPU-only.

## Environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python download_yunet.py
python download_model.py
copy .env.example .env   # SERPAPI_KEY=<key from https://serpapi.com/>
```

`requirements.txt` is pinned to pip wheels only (`opencv-python`, `numpy`, `onnxruntime`,
`streamlit`, `google-search-results`, `requests`, `python-dotenv`) — no compilers, no Node,
no API billing beyond SerpAPI's free tier.

## Reference run (Sept 2026)

- Query: `File:Virat Kohli in PMO New Delhi.jpg` (Wikimedia Commons), uploaded to
  `https://files.catbox.moe/i2ps9c.jpg`
- Command: `python search.py --url https://files.catbox.moe/i2ps9c.jpg`
- Result: 5 `visual_matches` — Reddit r/RCB thread, Instagram `p/DUBKXklEtwR`, Wikimedia
  Commons file page, X `@RcbianOfficial` status, Vükiped article — saved to
  `candidates.json` (committed), thumbnails to `gallery/` (gitignored).
- Ranking: `find_best('input.jpg', gallery/*.jpg)` → best `candidate_4.jpg`,
  similarity 0.951, verified True; full ranking in README.
- Ledger: `anchor()` → `verify()` True, tampered fingerprint → False,
  `verify_chain()` True.

## Re-running offline

Delete nothing: with `candidates.json` committed, `Search` falls back to cache when the
API is unreachable, and the ledger needs no network at all. Delete `chain.json` before a
fresh recording so blocks restart at 0.

## Costs

SerpAPI free tier: 100 searches/month, no card. Reference testing burned ~3. Model
weights: YuNet ~230 KB, ArcFace ~167 MB (gitignored, fetched by the download scripts).
