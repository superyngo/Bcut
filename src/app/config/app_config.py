import sys, os
from pathlib import Path
from typing import LiteralString
from enum import StrEnum, auto
from ..utils.mytypes import PathEnum

# Get the parent directory of the current
runtime_pth = Path(os.path.abspath(sys.argv[0])).parent

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""
os.environ["PYTHONUTF8"] = "1"

__all__: list[str] = ["Actions", "AppPaths"]


# set app name
APP_NAME: LiteralString = "BCut"


class Actions(StrEnum):
    """_summary_

    Args:
        StrEnum (_type_): _description_
    """

    CONVERTER = auto()
    SPEEDUP = auto()
    UPLOADER = auto()


# set app base path
class AppPaths(PathEnum):
    RUNTIME_PATH = runtime_pth
    PROGRAM_DATA = Path(os.environ["PROGRAMDATA"]) / APP_NAME  # C:\ProgramData
    APP_DATA = Path(os.environ["APPDATA"]) / APP_NAME  # C:\Users\user\AppData\Roaming
    CONFIG = APP_DATA / "config.conf"
    LOGS = APP_DATA / "Logs"
