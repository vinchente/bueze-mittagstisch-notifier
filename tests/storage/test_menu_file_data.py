import logging
from pathlib import Path

import pytest

from bueze_mittagstisch_notifier.config import settings
from bueze_mittagstisch_notifier.storage.menu_file_data import MenuArchive
from tests.conftest import (
    TEST_MENU_FILE_DATA_1,
    TEST_MENU_FILE_DATA_2,
    TEST_MENU_FILE_DATA_3,
    TEST_MENU_FILE_DATA_4,
)

LOGGER = logging.getLogger(__name__)

TEST_INITIAL_STORED_FILENAMES = {
    TEST_MENU_FILE_DATA_1.filename,
    TEST_MENU_FILE_DATA_2.filename,
}


@pytest.mark.parametrize("initial_filenames", [set(), TEST_INITIAL_STORED_FILENAMES])
def test_load_filenames_and_update_menu_file_data(
    tmp_path: Path, initial_filenames: set[str]
) -> None:
    file_path = tmp_path / settings.menu_archive.name
    menu_archive = MenuArchive(menu_archive_path=file_path)

    if initial_filenames:
        menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_1)
        menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_2)

    initial_filenames_result = menu_archive.load_filenames()
    assert initial_filenames_result == initial_filenames

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_3)
    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_4)

    updated_filenames_result = menu_archive.load_filenames()
    initial_filenames.update(
        {TEST_MENU_FILE_DATA_3.filename, TEST_MENU_FILE_DATA_4.filename}
    )
    assert updated_filenames_result == initial_filenames


def test_update_menu_archive(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("INFO")
    file_path = tmp_path / settings.menu_archive.name
    menu_archive = MenuArchive(menu_archive_path=file_path)

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_3)
    menu_file_data_set = menu_archive.load_menu_archive()
    assert TEST_MENU_FILE_DATA_3 in menu_file_data_set

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_4)
    menu_file_data_set = menu_archive.load_menu_archive()
    assert TEST_MENU_FILE_DATA_3 in menu_file_data_set
    assert TEST_MENU_FILE_DATA_4 in menu_file_data_set

    assert "Menu archive updated with menu-3.png" in caplog.text
    assert "Menu archive updated with menu-4.png" in caplog.text
