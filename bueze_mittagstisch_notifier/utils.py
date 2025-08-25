from pathlib import Path


def get_filenames_path(filenames_json: str) -> Path:
    return Path(__file__).parent.parent / "data" / filenames_json
