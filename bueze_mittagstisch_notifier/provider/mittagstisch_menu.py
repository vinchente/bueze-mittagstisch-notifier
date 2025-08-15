import logging
from typing import Optional

from bueze_mittagstisch_notifier.adapters.bueze import BuezeAdapter

LOGGER = logging.getLogger(__name__)


class MittagstischMenuProvider:
    def __init__(self, bueze_adapter: BuezeAdapter) -> None:
        self._bueze_adapter = bueze_adapter

    def get_and_save_menu(
        self,
        output_dir: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> None:
        menu_binaries, original_file_name = self._bueze_adapter.get_menu_binary_data()

        if not file_name:
            file_name = original_file_name

        if output_dir:
            output_path = output_dir + "/" + file_name
        else:
            output_path = file_name

        with open(output_path, "wb") as f:
            f.write(menu_binaries)
        LOGGER.info(f"Menu downloaded to {output_path}")
