# Security & responsible use — FaceTrace

- **API keys are never committed.** `.env` is gitignored; `.env.example` holds only the
  placeholder. The Streamlit key field is `type="password"` and `load_dotenv()` prefers
  the environment. If a key leaks, revoke it at serpapi.com and burn a new one.
- **No private-data pipeline.** The app stores only what Lens already publishes
  (titles, links, thumbnails) plus local SHA-256 hashes. No scraping of login-walled
  content, no PimEyes-style bypasses, no face database of non-consenting people.
- **Public-figure scope.** Reference demo uses a widely published public figure.
  Do not point FaceTrace at strangers, minors, or non-consenting individuals —
  that violates the spirit of the task and likely the platforms' ToS.
- **Ledger honesty.** `chain.json` is a local tamper-evident log, described as such
  everywhere (README, UI copy, release notes). It is not marketed as mainnet-grade
  decentralization.
- **Reporting issues:** open a GitHub issue; do not attach API keys, private photos,
  or personal data to reports.
