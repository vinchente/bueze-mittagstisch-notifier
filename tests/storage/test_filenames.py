import json
import logging
from pathlib import Path

import pytest

from bueze_mittagstisch_notifier.config import settings
from bueze_mittagstisch_notifier.storage.filenames import (
    load_seen_files,
    save_seen_files,
    update_seen_filenames,
)

LOGGER = logging.getLogger(__name__)

TEST_INITIAL_STORED_FILENAMES = {"menu-1.png", "menu-2.png"}


@pytest.mark.parametrize("initial_filenames", [None, TEST_INITIAL_STORED_FILENAMES])
def test_load_and_save_seen_files(
    tmp_path: Path, initial_filenames: set[str] | None
) -> None:
    file_path = tmp_path / settings.filenames_storage.name

    if initial_filenames is not None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(list(initial_filenames), f)

    loaded = load_seen_files(file_path)
    assert loaded == (initial_filenames or set())

    new_filenames = {"menu-3.png", "menu-4.png"}
    save_seen_files(new_filenames, file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        saved_data = set(json.load(f))
    assert saved_data == new_filenames


def test_update_seen_filenames(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level("INFO")

    file_path = tmp_path / "seen_files.json"

    update_seen_filenames("menu-3.png", file_path)
    data = load_seen_files(file_path)
    assert "menu-3.png" in data

    update_seen_filenames("menu-4.png", file_path)
    data = load_seen_files(file_path)
    assert data == {"menu-3.png", "menu-4.png"}

    assert "Filenames file updated with menu-3.png" in caplog.text
    assert "Filenames file updated with menu-4.png" in caplog.text
