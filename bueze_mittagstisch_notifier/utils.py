import logging
from datetime import datetime
from pathlib import Path
from typing import Union
from zoneinfo import ZoneInfo

LOGGER = logging.getLogger(__name__)


def get_menu_archive_path(menu_archive_name: str) -> Path:
    return Path(__file__).parent.parent / "data" / menu_archive_name


def setup_logging_console(
    *,
    level: Union[int, str],
) -> None:
    logger = logging.getLogger()
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


def parse_http_date_to_datetime(last_modified_string: str) -> datetime:
    return datetime.strptime(last_modified_string, "%a, %d %b %Y %H:%M:%S GMT").replace(
        tzinfo=ZoneInfo("UTC")
    )
