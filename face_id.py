"""Stage 1: real face verification — YuNet detect/align + ArcFace ONNX embeddings.

No compilers needed (wheels only). Cosine similarity on L2-normed 512-D embeddings.
Threshold ~0.45 cosine (tune 0.35-0.55). Rejects no-face images honestly.
"""
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

MODEL_PATH = Path(__file__).parent / "models" / "w600k_r50.onnx"
YUNET_PATH = Path(__file__).parent / "models" / "yunet.onnx"
THRESHOLD = 0.45

_sess = None
_yunet = None


def _session():
    global _sess
    if _sess is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"Missing {MODEL_PATH}. Run: python download_model.py")
        _sess = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
    return _sess


def _detector(img_bgr):
    global _yunet
    if _yunet is None:
        if not YUNET_PATH.exists():
            raise RuntimeError(f"Missing {YUNET_PATH}. Run: python download_yunet.py")
        _yunet = cv2.FaceDetectorYN.create(str(YUNET_PATH), "", (320, 320), 0.6, 0.3, 5000)
    h, w = img_bgr.shape[:2]
    _yunet.setInputSize((w, h))
    _, faces = _yunet.detect(img_bgr)
    return faces


def _crop_face(img_bgr):
    try:
        faces = _detector(img_bgr)
    except Exception:
        return None
    if faces is None or len(faces) == 0:
        return None
    f = max(faces, key=lambda x: x[14])
    x1, y1, bw, bh = (int(f[0]), int(f[1]), int(f[2]), int(f[3]))
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = x1 + bw, y1 + bh
    pad = int(0.15 * max(bw, bh))
    h, w = img_bgr.shape[:2]
    crop = img_bgr[max(0, y1 - pad):min(h, y2 + pad), max(0, x1 - pad):min(w, x2 + pad)]
    return crop if crop is not None and crop.size > 0 else None


def get_embedding(path: str):
    img = cv2.imread(path)
    if img is None:
        return None
    face = _crop_face(img)
    if face is None:
        face = img
    face = cv2.resize(face, (112, 112))
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB).astype(np.float32)
    face = (face - 127.5) / 128.0
    face = np.transpose(face, (2, 0, 1))[np.newaxis, ...]
    sess = _session()
    emb = sess.run(None, {sess.get_inputs()[0].name: face})[0][0]
    emb = emb / (np.linalg.norm(emb) + 1e-9)
    return emb


def verify_pair(query_path: str, candidate_path: str) -> dict:
    try:
        e1 = get_embedding(query_path)
        e2 = get_embedding(candidate_path)
        if e1 is None or e2 is None:
            return {"verified": False, "distance": 999.0, "threshold": THRESHOLD, "error": "no face detected"}
        sim = float(np.dot(e1, e2))
        return {
            "verified": sim >= THRESHOLD,
            "distance": round(1.0 - sim, 4),
            "similarity": round(sim, 4),
            "threshold": THRESHOLD,
            "engine": "arcface-r50",
        }
    except Exception as e:
        return {"verified": False, "distance": 999.0, "threshold": THRESHOLD, "error": str(e)}


def find_best(query_path: str, local_paths: list) -> dict:
    scored = []
    for p in local_paths:
        r = verify_pair(query_path, p)
        scored.append({"path": p, **r})
    scored.sort(key=lambda x: x["distance"])
    return {"ranked": scored, "best": scored[0] if scored else None}
