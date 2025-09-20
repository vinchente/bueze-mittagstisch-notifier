import base64
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, field_serializer, field_validator

LOGGER = logging.getLogger(__name__)


class MenuFileData(BaseModel):
    url: str
    filename: str
    upload_time: datetime
    content: bytes

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content).hexdigest()

    @field_serializer("content")
    def serialize_content(self, v: bytes) -> str:
        return base64.b64encode(v).decode("ascii")

    @field_validator("content", mode="before")
    def deserialize_content(cls, v: Union[str, bytes]) -> bytes:
        if isinstance(v, str):
            return base64.b64decode(v)
        return v

    model_config = {"frozen": True}


class MenuArchive:
    def __init__(self, menu_archive_path: Path):
        self._menu_archive_path = menu_archive_path
        self.files: dict[str, list[MenuFileData]] = {}
        self.latest_upload_time: Optional[datetime] = None

    def load_menu_archive(self) -> set[MenuFileData]:
        if self._menu_archive_path.exists():
            with open(self._menu_archive_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            menu_file_data_set = {MenuFileData.model_validate(d) for d in data}
            return menu_file_data_set
        return set()

    def update_menu_archive(self, menu_file_data: MenuFileData) -> None:
        seen_menu_file_data_set = self.load_menu_archive()
        seen_menu_file_data_set.add(menu_file_data)
        self._save_menu_file_data_set(menu_file_data_set=seen_menu_file_data_set)

    def get_most_recent_archived_menu_upload_time(self) -> Optional[datetime]:
        if self._menu_archive_path.exists():
            seen_menu_file_data_set = self.load_menu_archive()
            most_recent_time = max(
                [
                    menu_file_data.upload_time
                    for menu_file_data in seen_menu_file_data_set
                ]
            )
            return most_recent_time
        return None

    def contains(self, menu_file_data: MenuFileData) -> bool:
        seen_menu_file_data_set = self.load_menu_archive()
        return any(m.hash == menu_file_data.hash for m in seen_menu_file_data_set)

    def _save_menu_file_data_set(self, menu_file_data_set: set[MenuFileData]) -> None:
        self._menu_archive_path.parent.mkdir(parents=True, exist_ok=True)
        json_serialized_menu_file_data_set = [
            m.model_dump(mode="json") for m in menu_file_data_set
        ]
        with open(self._menu_archive_path, "w", encoding="utf-8") as f:
            json.dump(
                json_serialized_menu_file_data_set,
                f,
                indent=2,
            )
