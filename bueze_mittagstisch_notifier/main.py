import asyncio
import logging

from config import settings, setup_logging_console

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier
from bueze_mittagstisch_notifier.scheduler.scheduler import Scheduler

LOGGER = logging.getLogger(__name__)


def main() -> None:
    LOGGER.info("Hello from bueze-mittagstisch-notifier!")

    bueze_adapter = BuezeAdapter(page_url=settings.bueze.page_url)
    telegram_notifier = TelegramNotifier(telegram_config=settings.telegram)
    scheduler = Scheduler(
        bueze_adapter=bueze_adapter, telegram_notifier=telegram_notifier
    )

    asyncio.run(scheduler.run())


if __name__ == "__main__":
    setup_logging_console(level=logging.INFO)
    main()
