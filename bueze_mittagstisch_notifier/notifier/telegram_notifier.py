import asyncio
import logging

from telegram import Bot

from bueze_mittagstisch_notifier.config import TelegramConfig

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, telegram_config: TelegramConfig) -> None:
        self._bot = Bot(token=telegram_config.bot.token.get_secret_value())
        self._channel_id = telegram_config.channel_id

    def send_mittagstisch_menu_notification(self, menu_image: bytes) -> None:
        asyncio.run(self._send_image_to_channel(image=menu_image))

    async def _send_image_to_channel(self, image: bytes) -> None:
        await self._bot.send_photo(
            chat_id=self._channel_id,
            photo=image,
            caption="Here is the new Mittagstisch plan for the week!",
        )
