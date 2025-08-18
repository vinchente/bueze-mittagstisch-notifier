import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import BuezeAdapter
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier

LOGGER = logging.getLogger(__name__)

BERLIN = ZoneInfo("Europe/Berlin")


class Scheduler:
    def __init__(
        self,
        bueze_adapter: BuezeAdapter,
        telegram_notifier: TelegramNotifier,
        check_interval: int = 300,
    ) -> None:
        self._bueze_adapter = bueze_adapter
        self._telegram_notifier = telegram_notifier
        self._check_interval = check_interval
        self._sent_filenames: set[str] = set()

    async def wait_until_monday_10am(self) -> None:
        while True:
            now = datetime.now(tz=BERLIN)
            days_ahead = (7 - now.weekday()) % 7
            target = (now + timedelta(days=days_ahead)).replace(
                hour=10, minute=28, second=30, microsecond=0
            )
            if target <= now:
                target += timedelta(days=7)
            wait_seconds = (target - now).total_seconds()
            LOGGER.info(f"Sleeping until {target}...")
            await asyncio.sleep(wait_seconds)
            return

    async def run(self) -> None:
        while True:
            await self.wait_until_monday_10am()
            LOGGER.info("Checking for new menu...")

            while True:
                try:
                    menu_image, filename = (
                        self._bueze_adapter.get_menu_binary_data_and_file_name()
                    )

                    if filename not in self._sent_filenames:
                        LOGGER.info(f"New menu found: {filename}")
                        await (
                            self._telegram_notifier.send_mittagstisch_menu_notification(
                                menu_image=menu_image
                            )
                        )
                        self._sent_filenames.add(filename)
                        break
                    else:
                        LOGGER.info(f"{filename} already sent, retrying...")
                except httpx.HTTPError as e:
                    LOGGER.error(f"Network error: {e}, retrying...")

                await asyncio.sleep(self._check_interval)
