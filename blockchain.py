"""Stage 3: simulated hash-chained ledger (stdlib only, offline-safe).

Each anchor creates a block: {index, timestamp, fingerprint, prev_hash, block_hash}.
block_hash = SHA256(index|timestamp|fingerprint|prev_hash) — tamper-evident, re-verifiable.
Meets task rule: local/simulated chain allowed with on-chain re-verification demo.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CHAIN_FILE = Path(__file__).parent / "chain.json"


def _load_chain() -> list:
    if CHAIN_FILE.exists():
        try:
            return json.loads(CHAIN_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_chain(chain: list) -> None:
    CHAIN_FILE.write_text(json.dumps(chain, indent=2), encoding="utf-8")


def fingerprint(post: dict) -> str:
    canonical = json.dumps(post, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def image_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def anchor(fingerprint_hex: str) -> dict:
    chain = _load_chain()
    prev_hash = chain[-1]["block_hash"] if chain else "0" * 64
    index = len(chain)
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = f"{index}|{timestamp}|{fingerprint_hex.lower()}|{prev_hash}"
    block_hash = hashlib.sha256(payload.encode()).hexdigest()
    block = {
        "index": index,
        "timestamp": timestamp,
        "fingerprint": fingerprint_hex.lower(),
        "prev_hash": prev_hash,
        "block_hash": block_hash,
    }
    chain.append(block)
    _save_chain(chain)
    return {"tx_hash": block_hash, "block": index}


def verify(fingerprint_hex: str, tx_hash: str) -> bool:
    chain = _load_chain()
    for b in chain:
        if b.get("block_hash", "").lower() == tx_hash.lower():
            if b.get("fingerprint", "").lower() != fingerprint_hex.lower():
                return False
            payload = f"{b['index']}|{b['timestamp']}|{b['fingerprint']}|{b['prev_hash']}"
            return hashlib.sha256(payload.encode()).hexdigest().lower() == tx_hash.lower()
    return False


def verify_chain() -> bool:
    chain = _load_chain()
    prev = "0" * 64
    for b in chain:
        if b.get("prev_hash") != prev:
            return False
        payload = f"{b['index']}|{b['timestamp']}|{b['fingerprint']}|{b['prev_hash']}"
        if hashlib.sha256(payload.encode()).hexdigest().lower() != b.get("block_hash", "").lower():
            return False
        prev = b["block_hash"]
    return True
