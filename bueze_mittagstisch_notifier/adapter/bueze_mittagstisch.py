import logging
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

from bueze_mittagstisch_notifier.storage.menu_file_data import MenuFileData
from bueze_mittagstisch_notifier.utils import parse_http_date_to_datetime

LOGGER = logging.getLogger(__name__)


class LinkTagNotFoundError(Exception):
    pass


class BuezeAdapter:
    def __init__(self, page_url: str) -> None:
        self._page_url = page_url

    def get_last_menu_upload_time(self) -> datetime:
        menu_url = self.get_menu_url()
        with httpx.Client() as client:
            head_resp = client.head(menu_url)
            last_modified_string = head_resp.headers.get("Last-Modified")
        return parse_http_date_to_datetime(last_modified_string=last_modified_string)

    def get_menu_file_data(self) -> MenuFileData:
        menu_url = self.get_menu_url()
        filename = menu_url.rsplit("/", 1)[-1]

        with httpx.Client() as client:
            png_resp = client.get(menu_url)
            png_resp.raise_for_status()

        return MenuFileData(
            url=menu_url,
            filename=filename,
            upload_time=parse_http_date_to_datetime(
                last_modified_string=png_resp.headers.get("Last-Modified")
            ),
            content=png_resp.content,
        )

    def get_menu_url(self) -> str:
        with httpx.Client() as client:
            resp = client.get(self._page_url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        link = soup.find(
            "a",
            href=lambda h: isinstance(h, str) and h.lower().endswith((".png", ".pdf")),
        )
        if not isinstance(link, Tag):
            raise LinkTagNotFoundError(
                "No <a> tag with an href ending with '.png' or '.pdf' found on the page."
            )
        href = link.get("href")

        if not isinstance(href, str):
            if not href:
                raise ValueError("Link tag has no href attribute")
            raise RuntimeError("Found <a> tag without a valid href")

        png_url = urljoin(self._page_url, href)
        return png_url

    def get_and_save_menu(
        self,
        output_dir: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> None:
        menu_data = self.get_menu_file_data()

        if not file_name:
            file_name = menu_data.filename

        if output_dir:
            output_path = output_dir + "/" + file_name
        else:
            output_path = file_name

        with open(output_path, "wb") as f:
            f.write(menu_data.content)
        LOGGER.info(f"Menu downloaded to {output_path}")
