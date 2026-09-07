"""Download YuNet ONNX face detector (OpenCV DNN, wheel-only, no compilers)."""
import urllib.request
from pathlib import Path

URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
DEST = Path(__file__).parent / "models" / "yunet.onnx"
DEST.parent.mkdir(exist_ok=True)
print("downloading YuNet (~300KB)...")
urllib.request.urlretrieve(URL, DEST)
print("saved", DEST, DEST.stat().st_size, "bytes")
