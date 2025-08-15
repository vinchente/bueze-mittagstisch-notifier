from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

PAGE_URL = "https://bueze.de/unser-mittagstisch/"


def fetch_menu_png(page_url: str, output_path: str = "menu2.png") -> None:
    with httpx.Client() as client:
        resp = client.get(page_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        link = soup.find(
            "a", href=lambda h: isinstance(h, str) and h.lower().endswith(".png")
        )
        if not isinstance(link, Tag):
            raise RuntimeError(
                "No <a> tag with an href ending in .png found on the page."
            )
        href = link.get("href")

        if not isinstance(href, str):
            if not href:
                raise RuntimeError("Link tag has no href attribute")
            raise RuntimeError("Found <a> tag without a valid href")

        png_url = urljoin(page_url, href)
        print(f"Found PNG URL: {png_url}")

        png_resp = client.get(png_url)
        png_resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(png_resp.content)
        print(f"Menu downloaded to {output_path}")


def main() -> None:
    print("Hello from bueze-mittagstisch-notifier!")
    fetch_menu_png(PAGE_URL)


if __name__ == "__main__":
    main()
