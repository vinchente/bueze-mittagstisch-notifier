import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from time import sleep
from typing import Optional
from zoneinfo import ZoneInfo

import httpx

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
    LinkTagNotFoundError,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier
from bueze_mittagstisch_notifier.storage.menu_file_data import (
    MenuArchive,
)

LOGGER = logging.getLogger(__name__)

BERLIN = ZoneInfo("Europe/Berlin")
SECONDS_PER_HOUR = 3600
LOGGING_INTERVAL_IN_SECONDS_WHILE_WAITING = 3600


@dataclass(frozen=True)
class ScheduledCheck:
    weekday: int  # 0=Monday, 6=Sunday
    time_of_day: time


MENU_CHECK = ScheduledCheck(weekday=0, time_of_day=time(hour=10, minute=0))


class MenuCheckScheduler:
    def __init__(
        self,
        bueze_adapter: BuezeAdapter,
        telegram_notifier: TelegramNotifier,
        menu_archive: MenuArchive,
        check_interval: float = 300,
    ) -> None:
        self._bueze_adapter = bueze_adapter
        self._telegram_notifier = telegram_notifier
        self._menu_archive = menu_archive
        self._check_interval_seconds = check_interval

    async def run(self, max_iterations: Optional[int] = None) -> None:
        iterations = 0
        while max_iterations is None or iterations < max_iterations:
            _wait_until_next_time_to_start_check_loop()
            LOGGER.info("Checking for new menu...")

            await self._check_continuously_for_new_menu()

            iterations += 1

    async def _check_continuously_for_new_menu(self) -> None:
        while True:
            try:
                if self._new_menu_is_available():
                    menu_file_data = self._bueze_adapter.get_menu_file_data()
                    LOGGER.info(f"New menu found: {menu_file_data.filename}")
                    await self._telegram_notifier.send_mittagstisch_menu_notification(
                        menu_image=menu_file_data.content
                    )
                    self._menu_archive.update_menu_archive(
                        menu_file_data=menu_file_data,
                    )
                    break
                else:
                    LOGGER.info("No new menu found, checking again later...")

            except LinkTagNotFoundError as e:
                LOGGER.error(f"LinkTagNotFoundError: {e}")
            except httpx.RequestError as e:
                LOGGER.error(f"Network error: {e}, retrying...")
            except httpx.HTTPStatusError as e:
                LOGGER.warning(f"HTTP error: {e.response.status_code}")

            await asyncio.sleep(self._check_interval_seconds)

    def _new_menu_is_available(self) -> bool:
        most_recent_menu_upload_time = self._bueze_adapter.get_last_menu_upload_time()
        most_recent_archived_menu_upload_time = (
            self._menu_archive.get_most_recent_archived_menu_upload_time()
        )
        if most_recent_archived_menu_upload_time is None:
            return True
        else:
            return most_recent_archived_menu_upload_time < most_recent_menu_upload_time


def _wait_until_next_time_to_start_check_loop() -> None:
    next_menu_check = _get_next_menu_check_time(scheduled_check=MENU_CHECK)
    seconds_to_wait_for = (next_menu_check - datetime.now(tz=BERLIN)).total_seconds()

    LOGGER.info(f"Sleeping until {next_menu_check}...")

    _wait_with_periodic_logging(
        wait_seconds=seconds_to_wait_for,
        logging_interval_seconds=LOGGING_INTERVAL_IN_SECONDS_WHILE_WAITING,
    )


def _get_next_menu_check_time(scheduled_check: ScheduledCheck) -> datetime:
    now = datetime.now(tz=BERLIN)
    days_ahead = (scheduled_check.weekday - now.weekday()) % 7

    next_menu_check = (now + timedelta(days=days_ahead)).replace(
        hour=scheduled_check.time_of_day.hour,
        minute=scheduled_check.time_of_day.minute,
        second=0,
        microsecond=0,
    )

    if next_menu_check <= now:
        next_menu_check += timedelta(days=7)

    return next_menu_check


def _wait_with_periodic_logging(
    wait_seconds: float, logging_interval_seconds: float
) -> None:
    while wait_seconds > 0:
        sleep_seconds = min(logging_interval_seconds, wait_seconds)
        sleep(sleep_seconds)
        wait_seconds -= sleep_seconds
        remaining_hours = wait_seconds / SECONDS_PER_HOUR

        LOGGER.info(f"{remaining_hours:.2f} hours remaining until next menu check")
