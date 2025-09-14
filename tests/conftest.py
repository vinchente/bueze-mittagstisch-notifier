from pathlib import Path

import pytest
from dotenv import load_dotenv

from bueze_mittagstisch_notifier.storage.menu_file_data import MenuFileData
from bueze_mittagstisch_notifier.utils import parse_http_date_to_datetime

load_dotenv(dotenv_path=Path(__file__).parent / "pytest.env")

TEST_MENU_FILE_DATA_1 = MenuFileData(
    url="https://bueze-test.de/menu-1.png",
    filename="menu-1.png",
    upload_time=parse_http_date_to_datetime("Fri, 1 Sep 2025 10:15:30 GMT"),
    content=b"fake-png-bytes-1",
)
TEST_MENU_FILE_DATA_2 = MenuFileData(
    url="https://bueze-test.de/menu-2.png",
    filename="menu-2.png",
    upload_time=parse_http_date_to_datetime("Fri, 2 Sep 2025 10:15:30 GMT"),
    content=b"fake-png-bytes-2",
)
TEST_MENU_FILE_DATA_3 = MenuFileData(
    url="https://bueze-test.de/menu-3.png",
    filename="menu-3.png",
    upload_time=parse_http_date_to_datetime("Fri, 3 Sep 2025 10:15:30 GMT"),
    content=b"fake-png-bytes-3",
)
TEST_MENU_FILE_DATA_4 = MenuFileData(
    url="https://bueze-test.de/menu-4.png",
    filename="menu-4.png",
    upload_time=parse_http_date_to_datetime("Fri, 4 Sep 2025 10:15:30 GMT"),
    content=b"fake-png-bytes-4",
)


@pytest.fixture
def test_menu_image() -> bytes:
    return b"fake-png-bytes"
