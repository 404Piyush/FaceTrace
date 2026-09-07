"""Stage 1: face verification.

Primary: DeepFace (Facenet512, cosine). Fallback: OpenCV histogram comparison when
DeepFace/TF is not installed (keeps Streamlit demo runnable without the heavy stack).
Both return {verified, distance, threshold} so app.py is unchanged.
"""
import cv2

try:
    from deepface import DeepFace

    HAVE_DEEPFACE = True
except Exception:
    HAVE_DEEPFACE = False

MODEL_NAME = "Facenet512"
DETECTOR = "retinaface"
DISTANCE_METRIC = "cosine"


def _hist_similarity(p1: str, p2: str) -> float:
    a = cv2.imread(p1)
    b = cv2.imread(p2)
    if a is None or b is None:
        return 0.0
    a = cv2.resize(a, (128, 128))
    b = cv2.resize(b, (128, 128))
    ha = cv2.calcHist([a], [0, 1, 2], None, [16, 16, 16], [0, 256] * 3)
    hb = cv2.calcHist([b], [0, 1, 2], None, [16, 16, 16], [0, 256] * 3)
    cv2.normalize(ha, ha)
    cv2.normalize(hb, hb)
    return float(cv2.compareHist(ha, hb, cv2.HISTCMP_CORREL))


def verify_pair(query_path: str, candidate_path: str) -> dict:
    if HAVE_DEEPFACE:
        try:
            res = DeepFace.verify(
                img1_path=query_path,
                img2_path=candidate_path,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR,
                distance_metric=DISTANCE_METRIC,
                enforce_detection=False,
            )
            return {
                "verified": bool(res.get("verified", False)),
                "distance": float(res.get("distance", 999.0)),
                "threshold": float(res.get("threshold", 0.40)),
            }
        except Exception as e:
            return {"verified": False, "distance": 999.0, "threshold": 0.40, "error": str(e)}
    try:
        sim = _hist_similarity(query_path, candidate_path)
        return {"verified": sim > 0.70, "distance": round(1.0 - sim, 3), "threshold": 0.30, "engine": "hist-fallback"}
    except Exception as e:
        return {"verified": False, "distance": 999.0, "threshold": 0.30, "error": str(e)}


def find_best(query_path: str, local_paths: list) -> dict:
    scored = []
    for p in local_paths:
        r = verify_pair(query_path, p)
        scored.append({"path": p, **r})
    scored.sort(key=lambda x: x["distance"])
    return {"ranked": scored, "best": scored[0] if scored else None}
