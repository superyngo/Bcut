from typing import TypedDict, NotRequired
from pathlib import Path
from ...services.my_driver.types import MyDriverConfig


class UploaderTask(TypedDict):
    name: str
    local_album_path: Path
    mkv_files: NotRequired[list[Path]]
    GPhoto_url: str
    browser_config: NotRequired[MyDriverConfig]
    delete_after: NotRequired[bool]
