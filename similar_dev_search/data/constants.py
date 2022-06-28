from pathlib import Path

N_JOBS = 4

BUILD_PATH = str(Path(__file__).parent.parent.parent / "build") + "/"
VENDOR_PATH = str(Path(__file__).parent.parent.parent / "vendor") + "/"
TEMP_PATH = str(Path(__file__).parent.parent.parent / "temp") + "/"

REPOS_PATH = str(Path(TEMP_PATH) / "repos") + "/"
JSONS_PATH = str(Path(TEMP_PATH) / "jsons") + "/"

language_names = [
    "python",
    "java",
    "javascript",
]
