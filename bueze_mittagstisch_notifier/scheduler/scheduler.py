import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import BuezeAdapter
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier
from bueze_mittagstisch_notifier.storage.filenames import (
    load_seen_files,
    update_seen_filenames,
)

LOGGER = logging.getLogger(__name__)

BERLIN = ZoneInfo("Europe/Berlin")


class Scheduler:
    def __init__(
        self,
        bueze_adapter: BuezeAdapter,
        telegram_notifier: TelegramNotifier,
        filenames_path: Path,
        check_interval: int = 300,
    ) -> None:
        self._bueze_adapter = bueze_adapter
        self._telegram_notifier = telegram_notifier
        self._filenames_path = filenames_path
        self._check_interval = check_interval

    async def run(self, max_iterations: Optional[int] = None) -> None:
        iterations = 0
        while max_iterations is None or iterations < max_iterations:
            await _wait_until_monday_10am()
            LOGGER.info("Checking for new menu...")

            while True:
                try:
                    menu_image, filename = (
                        self._bueze_adapter.get_menu_binary_data_and_file_name()
                    )

                    if filename not in load_seen_files(
                        filenames_path=self._filenames_path
                    ):
                        LOGGER.info(f"New menu found: {filename}")
                        await (
                            self._telegram_notifier.send_mittagstisch_menu_notification(
                                menu_image=menu_image
                            )
                        )
                        update_seen_filenames(
                            filename=filename, filenames_path=self._filenames_path
                        )
                        break
                    else:
                        LOGGER.info(f"{filename} already sent, checking again later...")
                except httpx.HTTPError as e:
                    LOGGER.error(f"Network error: {e}, retrying...")

                await asyncio.sleep(self._check_interval)

            iterations += 1


async def _wait_until_monday_10am() -> None:
    while True:
        now = datetime.now(tz=BERLIN)
        days_ahead = (7 - now.weekday()) % 7
        target = (now + timedelta(days=days_ahead)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        if target <= now:
            target += timedelta(days=7)
        wait_seconds = (target - now).total_seconds()
        LOGGER.info(f"Sleeping until {target}...")
        await asyncio.sleep(wait_seconds)
        return
