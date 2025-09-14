import asyncio
import logging

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
)
from bueze_mittagstisch_notifier.config import settings
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier
from bueze_mittagstisch_notifier.scheduler.menu_check_scheduler import (
    MenuCheckScheduler,
)
from bueze_mittagstisch_notifier.storage.menu_file_data import MenuArchive
from bueze_mittagstisch_notifier.utils import (
    get_menu_archive_path,
    setup_logging_console,
)

LOGGER = logging.getLogger(__name__)


def main() -> None:
    LOGGER.info("Hello from bueze-mittagstisch-notifier!")

    bueze_adapter = BuezeAdapter(page_url=settings.bueze.page_url)
    telegram_notifier = TelegramNotifier(telegram_config=settings.telegram)
    menu_archive = MenuArchive(
        menu_archive_path=get_menu_archive_path(settings.menu_archive.name)
    )

    menu_check_scheduler = MenuCheckScheduler(
        bueze_adapter=bueze_adapter,
        telegram_notifier=telegram_notifier,
        menu_archive=menu_archive,
    )

    asyncio.run(menu_check_scheduler.run())


if __name__ == "__main__":
    setup_logging_console(level=logging.INFO)
    main()
