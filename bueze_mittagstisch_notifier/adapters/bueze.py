import logging
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

LOGGER = logging.getLogger(__name__)


class LinkTagNotFoundError(Exception):
    pass


class BuezeAdapter:
    def __init__(self, page_url: str) -> None:
        self._page_url = page_url

    def get_menu_url(self) -> str:
        with httpx.Client() as client:
            resp = client.get(self._page_url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        link = soup.find(
            "a", href=lambda h: isinstance(h, str) and h.lower().endswith(".png")
        )
        if not isinstance(link, Tag):
            raise LinkTagNotFoundError(
                "No <a> tag with an href ending with '.png' found on the page."
            )
        href = link.get("href")

        if not isinstance(href, str):
            if not href:
                raise ValueError("Link tag has no href attribute")
            raise RuntimeError("Found <a> tag without a valid href")

        png_url = urljoin(self._page_url, href)
        LOGGER.info(f"Found PNG URL: {png_url}")
        return png_url

    def get_menu_binary_data(self) -> tuple[bytes, str]:
        menu_url = self.get_menu_url()
        filename = menu_url.rsplit("/", 1)[-1]

        with httpx.Client() as client:
            png_resp = client.get(menu_url)
            png_resp.raise_for_status()

        return png_resp.content, filename
