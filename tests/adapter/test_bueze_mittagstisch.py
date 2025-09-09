from pathlib import Path

import httpx
import pytest
import respx
from _pytest.monkeypatch import MonkeyPatch

from bueze_mittagstisch_notifier.adapter.bueze_mittagstisch import (
    BuezeAdapter,
    LinkTagNotFoundError,
)

TEST_BUEZE_PAGE_URL = "https://bueze-test.de/menu"
TEST_MENU_URL = "https://bueze-test.de/menu.png"
TEST_MENU_BINARY_DATA = b"fakebinarymenudata"
TEST_MENU_FILENAME = "menu.png"

# def test_bueze_adapter()


@respx.mock
def test_get_menu_binary_data_and_file_name() -> None:
    adapter = BuezeAdapter(page_url=TEST_BUEZE_PAGE_URL)

    respx.get(TEST_BUEZE_PAGE_URL).mock(
        return_value=httpx.Response(
            200, text='<html><a href="menu.png">Download</a></html>'
        )
    )

    respx.get(TEST_MENU_URL).mock(
        return_value=httpx.Response(200, content=TEST_MENU_BINARY_DATA)
    )

    binary_data, filename = adapter.get_menu_binary_data_and_file_name()

    assert binary_data == TEST_MENU_BINARY_DATA
    assert filename == TEST_MENU_FILENAME


@respx.mock
def test_get_menu_url_not_found() -> None:
    adapter = BuezeAdapter(TEST_BUEZE_PAGE_URL)

    respx.get(TEST_BUEZE_PAGE_URL).mock(
        return_value=httpx.Response(200, text="<html><body>No link here</body></html>")
    )

    with pytest.raises(LinkTagNotFoundError):
        adapter.get_menu_url()


def test_get_and_save_menu(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    adapter = BuezeAdapter(TEST_BUEZE_PAGE_URL)

    monkeypatch.setattr(
        adapter,
        "get_menu_binary_data_and_file_name",
        lambda: (TEST_MENU_BINARY_DATA, TEST_MENU_FILENAME),
    )

    adapter.get_and_save_menu(output_dir=str(tmp_path))

    saved_file = tmp_path / TEST_MENU_FILENAME
    assert saved_file.exists()
    assert saved_file.read_bytes() == TEST_MENU_BINARY_DATA
