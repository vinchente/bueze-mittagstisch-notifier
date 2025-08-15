import httpx


def main() -> None:
    print("Hello from bueze-mittagstisch-notifier!")
    url = "https://bueze.de/wp-content/uploads/2025/08/Screenshot-2025-08-14-161035.png"

    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()  # raise an error if download failed

        with open("menu.png", "wb") as f:
            f.write(response.content)

    print("Menu downloaded.")


if __name__ == "__main__":
    main()
