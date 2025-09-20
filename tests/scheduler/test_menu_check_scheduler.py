import asyncio
from datetime import datetime
from pathlib import Path
from typing import Iterator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier
from bueze_mittagstisch_notifier.scheduler.menu_check_scheduler import (
    MenuCheckScheduler,
)
from bueze_mittagstisch_notifier.storage.menu_file_data import (
    MenuArchive,
    MenuFileData,
)
from tests.conftest import TEST_MENU_FILE_DATA_1, TEST_MENU_FILE_DATA_2

original_async_sleep = asyncio.sleep


@pytest.fixture
def mock_menu_sequence() -> Iterator[MenuFileData]:
    menu_file_data_in_order_of_appearance = [
        TEST_MENU_FILE_DATA_1,
        TEST_MENU_FILE_DATA_2,
    ]
    return iter(menu_file_data_in_order_of_appearance)


@pytest.fixture
def mock_upload_time_sequence() -> Iterator[datetime]:
    menu_file_data_in_order_of_appearance = [
        TEST_MENU_FILE_DATA_1.upload_time,
        TEST_MENU_FILE_DATA_1.upload_time,
        TEST_MENU_FILE_DATA_2.upload_time,
    ]
    return iter(menu_file_data_in_order_of_appearance)


@pytest.fixture
def mock_bueze_adapter(
    mock_menu_sequence: Iterator[MenuFileData],
    mock_upload_time_sequence: Iterator[datetime],
) -> Mock:
    mock_adapter = Mock(spec=BuezeAdapter)
    mock_adapter.get_menu_file_data.side_effect = lambda: next(mock_menu_sequence)
    mock_adapter.get_last_menu_upload_time.side_effect = lambda: next(
        mock_upload_time_sequence
    )

    return mock_adapter


@pytest.fixture
def mock_telegram_notifier() -> AsyncMock:
    return AsyncMock(spec=TelegramNotifier)


@pytest.fixture
def tmp_seen_filenames(tmp_path: Path) -> Path:
    return tmp_path / "seen_files.json"


@pytest.mark.asyncio
async def test_menu_check_scheduler_run(
    mock_bueze_adapter: Mock,
    mock_telegram_notifier: AsyncMock,
    tmp_seen_filenames: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("INFO")

    menu_check_scheduler = MenuCheckScheduler(
        bueze_adapter=mock_bueze_adapter,
        telegram_notifier=mock_telegram_notifier,
        menu_archive=MenuArchive(menu_archive_path=tmp_seen_filenames),
        check_interval=0.001,
    )

    with (
        patch(
            "bueze_mittagstisch_notifier.scheduler.menu_check_scheduler.sleep",
            return_value=None,
        ),
        patch("asyncio.sleep", new=lambda _: original_async_sleep(0)),
    ):
        await menu_check_scheduler.run(max_iterations=2)

    sent_menu_image_bytes = [
        call.kwargs["menu_image"]
        for call in mock_telegram_notifier.send_mittagstisch_menu_notification.await_args_list
    ]
    assert sent_menu_image_bytes == [
        TEST_MENU_FILE_DATA_1.content,
        TEST_MENU_FILE_DATA_2.content,
    ]

    menu_file_data_set = menu_check_scheduler._menu_archive.load_menu_archive()
    assert menu_file_data_set == {TEST_MENU_FILE_DATA_1, TEST_MENU_FILE_DATA_2}

    assert "New menu found: menu-1.png" in caplog.text
    assert "Menu archive updated with menu-1.png" in caplog.text
    assert "No new menu found, checking again later..." in caplog.text
    assert "New menu found: menu-2.png" in caplog.text
    assert "Menu archive updated with menu-2.png" in caplog.text
