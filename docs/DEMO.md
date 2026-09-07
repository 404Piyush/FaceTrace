# Demo script — FaceTrace 60-second recording

Target: one continuous screen recording, no edits. Show the terminal alongside the
browser for the genuineness proof. Tested flow as of v1.0.0.

## Before you press record

- [ ] `.venv` active, deps installed, `models/w600k_r50.onnx` + `models/yunet.onnx` present
- [ ] `.env` contains a SerpAPI key with ≥2 searches left (each Search click burns one)
- [ ] `chain.json` deleted so anchoring starts at block 0 (it is gitignored)
- [ ] Query image ready: the Virat Kohli Wikimedia photo, re-uploaded to catbox.moe
      for a fresh public URL (Lens rejects local paths and stale links)
- [ ] Terminal open next to the browser: `streamlit run app.py` visible

## The 60 seconds

| # | Do | Show / say |
|---|----|------------|
| 0:00 | Upload `input.jpg` | Query face thumbnail appears (240px, left panel) |
| 0:10 | Paste catbox URL, click **Search web for matching post** | Spinner → side-by-side query vs best match, `verified=True`, similarity ~0.95, clickable source-post link |
| 0:25 | Open the **SerpAPI matches JSON** expander | Raw `visual_matches` (Reddit, Instagram, X, Wikimedia, Vükiped) — this is the genuine-search proof, linger 5s |
| 0:35 | Click **Anchor on-chain** | Green confirmation: `tx=<64-hex> block=0 fp=<16-hex>…` |
| 0:45 | Click **Re-verify** | Green **MATCH block #0** + matching expected/recomputed fingerprints |
| 0:52 | Edit the snippet field (one word), click **Re-verify** | Red **FAIL: TAMPER DETECTED**, fingerprints differ |
| 0:58 | Restore snippet, click **Re-verify** | Green MATCH again — end recording |

## If something fails live

- **Lens errors / no key left:** the app warns and falls back to committed
  `candidates.json` automatically — narrate it ("falling back to cached search").
- **No Wi-Fi at all:** cached candidates + local ledger still complete the full arc.
- **Slow first embedding:** the ArcFace session warms on first verify (~seconds on CPU);
  click Search once before recording to warm it.
