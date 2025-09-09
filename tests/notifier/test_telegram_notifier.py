from unittest.mock import AsyncMock

import pytest
from _pytest.monkeypatch import MonkeyPatch

from bueze_mittagstisch_notifier.config import (
    settings,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier


@pytest.mark.asyncio
async def test_send_mittagstisch_menu_notification(
    monkeypatch: MonkeyPatch, test_menu_image: bytes
) -> None:
    fake_send_photo = AsyncMock()

    monkeypatch.setattr(
        "bueze_mittagstisch_notifier.notifier.telegram_notifier.Bot",
        lambda token: type("FakeBot", (), {"send_photo": fake_send_photo})(),
    )

    telegram_notifier = TelegramNotifier(telegram_config=settings.telegram)

    await telegram_notifier.send_mittagstisch_menu_notification(test_menu_image)

    fake_send_photo.assert_awaited_once_with(
        chat_id=settings.telegram.channel_id,
        photo=test_menu_image,
        caption="Here is the new Mittagstisch plan for the week!",
    )
