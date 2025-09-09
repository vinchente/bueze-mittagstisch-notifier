from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / "pytest.env")


@pytest.fixture
def test_menu_image() -> bytes:
    return b"fake-png-bytes"
