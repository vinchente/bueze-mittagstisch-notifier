from pathlib import Path

import httpx
import pytest
import respx
from _pytest.monkeypatch import MonkeyPatch

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
    LinkTagNotFoundError,
)
from bueze_mittagstisch_notifier.config import settings

TEST_MENU_URL = "https://bueze-test.de/menu.png"
TEST_MENU_FILENAME = "menu.png"


@respx.mock
def test_get_menu_binary_data_and_file_name(test_menu_image: bytes) -> None:
    adapter = BuezeAdapter(page_url=settings.bueze.page_url)

    respx.get(settings.bueze.page_url).mock(
        return_value=httpx.Response(
            200, text='<html><a href="menu.png">Download</a></html>'
        )
    )

    respx.get(TEST_MENU_URL).mock(
        return_value=httpx.Response(200, content=test_menu_image)
    )

    binary_data, filename = adapter.get_menu_binary_data_and_file_name()

    assert binary_data == test_menu_image
    assert filename == TEST_MENU_FILENAME


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
        "get_menu_binary_data_and_file_name",
        lambda: (test_menu_image, TEST_MENU_FILENAME),
    )

    adapter.get_and_save_menu(output_dir=str(tmp_path))

    saved_file = tmp_path / TEST_MENU_FILENAME
    assert saved_file.exists()
    assert saved_file.read_bytes() == test_menu_image
