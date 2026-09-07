# Contributing to FaceTrace

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python download_yunet.py
python download_model.py
copy .env.example .env   # add your own SERPAPI_KEY
```

## Workflow

1. Open an issue describing the change (bug, threshold tuning, new chain backend).
2. Branch from `main`: `git checkout -b <type>/<short-name>` (`feat/`, `fix/`, `docs/`).
3. Keep the stage seams intact: `search.py` returns `{title, link, thumbnail}` lists,
   `face_id.py` returns `{verified, distance, threshold}` dicts,
   `blockchain.py` keeps `fingerprint()/anchor()/verify()` signatures.
4. Verify before pushing:
   ```powershell
   .\.venv\Scripts\python.exe -m py_compile face_id.py app.py search.py blockchain.py
   ```
   plus one end-to-end `streamlit run app.py` pass (Search → Anchor → MATCH → tamper FAIL).
5. PR with: what changed, measured similarity/verify output, and any new limitations
   added to `docs/LIMITATIONS.md`.

## Ground rules

- Never commit `.env`, `chain.json`, `models/*.onnx`, `gallery/*.jpg`, or `input.jpg`
  (all gitignored). Never paste API keys into issues or code.
- Public/consenting faces in tests and demos only.
- Docs travel with code: behavior change → update README/docs in the same PR.
