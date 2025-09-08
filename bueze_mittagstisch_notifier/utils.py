import logging
from pathlib import Path
from typing import Union

LOGGER = logging.getLogger(__name__)


def get_filenames_path(filenames_json: str) -> Path:
    return Path(__file__).parent.parent / "data" / filenames_json


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
