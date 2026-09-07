"""Stage 2: genuine web search via SerpAPI Google Lens, top-5 + download."""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CANDIDATES_JSON = Path(__file__).parent / "candidates.json"
GALLERY_DIR = Path(__file__).parent / "gallery"
TOP_K = 5


def lens_search(public_image_url: str, api_key: str | None = None) -> list:
    from serpapi import GoogleSearch

    key = api_key or os.getenv("SERPAPI_KEY", "")
    if not key:
        raise RuntimeError("SERPAPI_KEY missing. Put it in .env or pass explicitly.")
    params = {"engine": "google_lens", "url": public_image_url, "api_key": key}
    res = GoogleSearch(params).get_dict()
    matches = res.get("visual_matches", []) or []
    out = []
    for m in matches[:TOP_K]:
        out.append({
            "title": m.get("title", ""),
            "link": m.get("link", ""),
            "thumbnail": m.get("thumbnail", m.get("image", "")),
        })
    CANDIDATES_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def load_cached() -> list:
    if CANDIDATES_JSON.exists():
        return json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))
    return []


def download_candidates(candidates: list) -> list:
    GALLERY_DIR.mkdir(exist_ok=True)
    local = []
    for i, c in enumerate(candidates):
        url = c.get("thumbnail", "")
        if not url:
            continue
        dest = GALLERY_DIR / f"candidate_{i}.jpg"
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            dest.write_bytes(r.content)
            local.append(str(dest))
        except Exception:
            continue
    return local


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="Public URL of query image (catbox.moe link)")
    args = ap.parse_args()
    cands = lens_search(args.url)
    print(json.dumps(cands, indent=2))
    print("downloaded:", download_candidates(cands))
