"""Download ArcFace ONNX (public buffalo_l w600k_r50) for real face embeddings."""
import urllib.request
from pathlib import Path

URL = "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
# Direct single-file mirror via huggingface (no auth):
FILE_URL = "https://huggingface.co/deepghs/insightface/resolve/main/buffalo_l/w600k_r50.onnx"
DEST = Path(__file__).parent / "models" / "w600k_r50.onnx"

DEST.parent.mkdir(exist_ok=True)
print("downloading ArcFace ONNX (~250MB)...")
urllib.request.urlretrieve(FILE_URL, DEST)
print("saved", DEST, DEST.stat().st_size, "bytes")
