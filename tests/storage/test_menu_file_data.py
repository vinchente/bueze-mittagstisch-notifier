import logging
from pathlib import Path

import pytest

from bueze_mittagstisch_notifier.config import settings
from bueze_mittagstisch_notifier.storage.menu_file_data import MenuArchive, MenuFileData
from tests.conftest import (
    TEST_MENU_FILE_DATA_1,
    TEST_MENU_FILE_DATA_2,
    TEST_MENU_FILE_DATA_3,
    TEST_MENU_FILE_DATA_4,
)

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def tmp_menu_archive_path(tmp_path: Path) -> Path:
    return tmp_path / settings.menu_archive.name


@pytest.mark.parametrize(
    "initial_menu_file_data_set",
    [set(), {TEST_MENU_FILE_DATA_1, TEST_MENU_FILE_DATA_2}],
)
def test_load_menu_archive_and_update_menu_file_data(
    tmp_menu_archive_path: Path, initial_menu_file_data_set: set[MenuFileData]
) -> None:
    menu_archive = MenuArchive(menu_archive_path=tmp_menu_archive_path)

    if initial_menu_file_data_set:
        menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_1)
        menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_2)

    initial_menu_file_data_set_result = menu_archive.load_menu_archive()
    assert initial_menu_file_data_set_result == initial_menu_file_data_set

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_3)
    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_4)

    updated_menu_file_data_set_result = menu_archive.load_menu_archive()
    initial_menu_file_data_set.update({TEST_MENU_FILE_DATA_3, TEST_MENU_FILE_DATA_4})
    assert updated_menu_file_data_set_result == initial_menu_file_data_set


def test_update_menu_archive(
    tmp_menu_archive_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    menu_archive = MenuArchive(menu_archive_path=tmp_menu_archive_path)

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_3)
    menu_file_data_set = menu_archive.load_menu_archive()
    assert TEST_MENU_FILE_DATA_3 in menu_file_data_set

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_4)
    menu_file_data_set = menu_archive.load_menu_archive()
    assert TEST_MENU_FILE_DATA_3 in menu_file_data_set
    assert TEST_MENU_FILE_DATA_4 in menu_file_data_set


def test_get_most_recent_archived_menu_upload_time(tmp_menu_archive_path: Path) -> None:
    menu_archive = MenuArchive(menu_archive_path=tmp_menu_archive_path)
    most_recent_archived_menu_upload_time = (
        menu_archive.get_most_recent_archived_menu_upload_time()
    )
    assert most_recent_archived_menu_upload_time is None

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_1)
    most_recent_archived_menu_upload_time = (
        menu_archive.get_most_recent_archived_menu_upload_time()
    )
    assert most_recent_archived_menu_upload_time == TEST_MENU_FILE_DATA_1.upload_time
    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_3)
    most_recent_archived_menu_upload_time = (
        menu_archive.get_most_recent_archived_menu_upload_time()
    )
    assert most_recent_archived_menu_upload_time == TEST_MENU_FILE_DATA_3.upload_time
    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_2)
    most_recent_archived_menu_upload_time = (
        menu_archive.get_most_recent_archived_menu_upload_time()
    )
    assert most_recent_archived_menu_upload_time == TEST_MENU_FILE_DATA_3.upload_time
    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_4)
    most_recent_archived_menu_upload_time = (
        menu_archive.get_most_recent_archived_menu_upload_time()
    )
    assert most_recent_archived_menu_upload_time == TEST_MENU_FILE_DATA_4.upload_time


def test_contains_check(tmp_menu_archive_path: Path) -> None:
    menu_archive = MenuArchive(menu_archive_path=tmp_menu_archive_path)

    assert not menu_archive.contains(menu_file_data=TEST_MENU_FILE_DATA_1)

    menu_archive.update_menu_archive(TEST_MENU_FILE_DATA_1)

    assert menu_archive.contains(menu_file_data=TEST_MENU_FILE_DATA_1)
    assert not menu_archive.contains(menu_file_data=TEST_MENU_FILE_DATA_2)
