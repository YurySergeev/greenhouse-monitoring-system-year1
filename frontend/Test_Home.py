from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMG_PATH = ASSETS_DIR / "greenhouse2.jpg"

def test_image_path():
    assert IMG_PATH.exists(), "Image file is missing"