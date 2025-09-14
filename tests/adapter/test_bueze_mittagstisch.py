import logging
from pathlib import Path

import httpx
import pytest
import respx
from _pytest.monkeypatch import MonkeyPatch

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
    LinkTagNotFoundError,
    MenuData,
)
from bueze_mittagstisch_notifier.config import settings
from bueze_mittagstisch_notifier.utils import parse_http_date_to_datetime

LOGGER = logging.getLogger(__name__)

TEST_MENU_URL = "https://bueze-test.de/menu.png"
TEST_MENU_FILENAME = "menu.png"
TEST_MENU_LAST_MODIFIED = "Fri, 12 Sep 2025 10:15:30 GMT"


@respx.mock
def test_get_last_menu_upload_time() -> None:
    respx.get(settings.bueze.page_url).mock(
        return_value=httpx.Response(
            200, text='<html><a href="menu.png">Download</a></html>'
        )
    )

    respx.head(TEST_MENU_URL).mock(
        return_value=httpx.Response(
            200,
            headers={"Last-Modified": TEST_MENU_LAST_MODIFIED},
        )
    )

    adapter = BuezeAdapter(page_url=settings.bueze.page_url)

    most_recent_menu_upload_time_result = adapter.get_last_menu_upload_time()

    most_recent_menu_upload_time_expected = parse_http_date_to_datetime(
        TEST_MENU_LAST_MODIFIED
    )
    assert most_recent_menu_upload_time_result == most_recent_menu_upload_time_expected


@respx.mock
def test_get_menu_data(test_menu_image: bytes) -> None:
    adapter = BuezeAdapter(page_url=settings.bueze.page_url)

    respx.get(settings.bueze.page_url).mock(
        return_value=httpx.Response(
            200, text='<html><a href="menu.png">Download</a></html>'
        )
    )

    respx.get(TEST_MENU_URL).mock(
        return_value=httpx.Response(
            200,
            content=test_menu_image,
            headers={"Last-Modified": TEST_MENU_LAST_MODIFIED},
        )
    )

    result_menu_data = adapter.get_menu_data()

    assert result_menu_data.content == test_menu_image
    assert result_menu_data.filename == TEST_MENU_FILENAME


@respx.mock
def test_get_menu_url_not_found() -> None:
    adapter = BuezeAdapter(page_url=settings.bueze.page_url)

    respx.get(settings.bueze.page_url).mock(
        return_value=httpx.Response(200, text="<html><body>No link here</body></html>")
    )

    with pytest.raises(LinkTagNotFoundError):
        adapter.get_menu_url()


def test_get_and_save_menu(
    tmp_path: Path, monkeypatch: MonkeyPatch, test_menu_image: bytes
) -> None:
    adapter = BuezeAdapter(page_url=settings.bueze.page_url)

    monkeypatch.setattr(
        adapter,
        "get_menu_data",
        lambda: MenuData(
            url=TEST_MENU_URL,
            filename=TEST_MENU_FILENAME,
            last_modified=TEST_MENU_LAST_MODIFIED,
            content=test_menu_image,
        ),
    )

    adapter.get_and_save_menu(output_dir=str(tmp_path))

    saved_file = tmp_path / TEST_MENU_FILENAME
    assert saved_file.exists()
    assert saved_file.read_bytes() == test_menu_image
