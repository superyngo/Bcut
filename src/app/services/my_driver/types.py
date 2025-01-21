from typing import TypedDict, NotRequired
from pathlib import Path


class MyDriverConfig(TypedDict):
    user_data_dir: NotRequired[Path]
    browser_executable_path: NotRequired[Path]
