import logging

from config import settings, setup_logging_console

from bueze_mittagstisch_notifier.adapters.bueze import BuezeAdapter
from bueze_mittagstisch_notifier.provider.mittagstisch_menu import (
    MittagstischMenuProvider,
)

LOGGER = logging.getLogger(__name__)


def main() -> None:
    LOGGER.info("Hello from bueze-mittagstisch-notifier!")
    mittagstisch_menu_provider = MittagstischMenuProvider(
        bueze_adapter=BuezeAdapter(page_url=settings.bueze.page_url)
    )
    mittagstisch_menu_provider.get_and_save_menu(file_name="menu3.png")


if __name__ == "__main__":
    setup_logging_console(level=logging.INFO)
    main()
