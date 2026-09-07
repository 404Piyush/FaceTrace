# Limitations — FaceTrace

Stated plainly so judges know what this is and isn't.

1. **Public-index only.** Google Lens returns publicly indexed images. Private
   Instagram/TikTok, login-walled albums, and unindexed faces return nothing. This is a
   platform constraint, not a bug — the demo scopes to public figures for this reason.
2. **Search budget.** SerpAPI free tier: 100 searches/month. Each *Search* click burns
   one; the committed `candidates.json` cache is the fallback.
3. **Demo-grade identity.** ArcFace R50 cosine at threshold 0.45 ranks and verifies
   well on the reference set (0.74–0.95) but is not a production identity system: angle,
   occlusion, heavy edits, and lookalikes can move scores across the line.
4. **Single-node ledger.** `chain.json` is tamper-evident (hash-chained, re-verified) but
   not distributed — no consensus, no independent validators. Credible as a
   verifiable record, not as a decentralized chain. EVM migration path is documented in
   ARCHITECTURE.md.
5. **Thumbnail fidelity.** Candidates are Lens thumbnails (low-res, cropped), which caps
   embedding quality versus full-resolution sources.
6. **Scope.** Public/consenting faces only. FaceTrace is a provenance demo, not a
   stranger-tracking tool (see SECURITY.md).
