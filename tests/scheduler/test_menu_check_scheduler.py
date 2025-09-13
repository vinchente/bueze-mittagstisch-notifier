import asyncio
from pathlib import Path
from typing import Iterator
from unittest.mock import AsyncMock, Mock, patch

import pytest

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
    MenuData,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier
from bueze_mittagstisch_notifier.scheduler.menu_check_scheduler import (
    MenuCheckScheduler,
)
from bueze_mittagstisch_notifier.storage.filenames import load_seen_files

original_async_sleep = asyncio.sleep


@pytest.fixture
def mock_menu_sequence() -> Iterator[MenuData]:
    menus_in_order_of_appearance = [
        MenuData(
            url="https://bueze-test.de/menu-1.png",
            filename="menu-1.png",
            last_modified="Fri, 5 Sep 2025 10:15:30 GMT",
            content=b"fake-png-bytes-1",
        ),
        MenuData(
            url="https://bueze-test.de/menu-1.png",
            filename="menu-1.png",
            last_modified="Fri, 5 Sep 2025 10:15:30 GMT",
            content=b"fake-png-bytes-1",
        ),
        MenuData(
            url="https://bueze-test.de/menu-1.png",
            filename="menu-2.png",
            last_modified="Fri, 12 Sep 2025 10:15:30 GMT",
            content=b"fake-png-bytes-2",
        ),
    ]
    return iter(menus_in_order_of_appearance)


@pytest.fixture
def mock_bueze_adapter(mock_menu_sequence: Iterator[MenuData]) -> Mock:
    mock_adapter = Mock(spec=BuezeAdapter)
    mock_adapter.get_menu_data.side_effect = lambda: next(mock_menu_sequence)

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
        filenames_path=tmp_seen_filenames,
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

    sent_menus = [
        call.kwargs["menu_image"]
        for call in mock_telegram_notifier.send_mittagstisch_menu_notification.await_args_list
    ]
    assert sent_menus == [b"fake-png-bytes-1", b"fake-png-bytes-2"]

    seen = load_seen_files(tmp_seen_filenames)
    assert seen == {"menu-1.png", "menu-2.png"}

    assert "New menu found: menu-1.png" in caplog.text
    assert "menu-1.png already sent, checking again later..." in caplog.text
    assert "New menu found: menu-2.png" in caplog.text
