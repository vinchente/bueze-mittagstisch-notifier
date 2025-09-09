import logging
from unittest.mock import AsyncMock, Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from bueze_mittagstisch_notifier.config import (
    settings,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier

LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_send_mittagstisch_menu_notification(
    monkeypatch: MonkeyPatch, test_menu_image: bytes
) -> None:
    mock_send_photo = AsyncMock()
    mock_bot = Mock()
    mock_bot.send_photo = mock_send_photo

    monkeypatch.setattr(
        "bueze_mittagstisch_notifier.notifier.telegram_notifier.Bot",
        lambda token: mock_bot,
    )

    telegram_notifier = TelegramNotifier(telegram_config=settings.telegram)

    await telegram_notifier.send_mittagstisch_menu_notification(test_menu_image)

    mock_send_photo.assert_awaited_once_with(
        chat_id=settings.telegram.channel_id,
        photo=test_menu_image,
        caption="Here is the new Mittagstisch plan for the week!",
    )
