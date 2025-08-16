import logging

from config import settings, setup_logging_console

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeMittagstischAdapter,
)
from bueze_mittagstisch_notifier.notifier.telegram_notifier import TelegramNotifier

LOGGER = logging.getLogger(__name__)


def main() -> None:
    LOGGER.info("Hello from bueze-mittagstisch-notifier!")
    bueze_mittagstisch_adapter = BuezeMittagstischAdapter(
        page_url=settings.bueze.page_url
    )
    menu_image, image_name = (
        bueze_mittagstisch_adapter.get_menu_binary_data_and_file_name()
    )

    telegram_notifier = TelegramNotifier(telegram_config=settings.telegram)
    telegram_notifier.send_mittagstisch_menu_notification(menu_image=menu_image)


if __name__ == "__main__":
    setup_logging_console(level=logging.INFO)
    main()
