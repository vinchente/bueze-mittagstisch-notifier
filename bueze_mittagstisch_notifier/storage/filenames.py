import json
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def load_seen_files(filenames_path: Path) -> set[str]:
    if filenames_path.exists():
        with open(filenames_path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen_files(filenames: set[str], filenames_path: Path) -> None:
    filenames_path.parent.mkdir(parents=True, exist_ok=True)
    with open(filenames_path, "w", encoding="utf-8") as f:
        json.dump(list(filenames), f, indent=2)


def update_seen_filenames(filename: str, filenames_path: Path) -> None:
    seen_files = load_seen_files(filenames_path=filenames_path)
    seen_files.add(filename)
    save_seen_files(filenames=seen_files, filenames_path=filenames_path)
    LOGGER.info(f"Filenames file updated with {filename}")
