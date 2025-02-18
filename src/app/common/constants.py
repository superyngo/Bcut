from re import A
import sys, os
from pathlib import Path
from typing import LiteralString
from enum import StrEnum, auto
from app.common.mytypes import PathEnum


__all__: list[str] = ["Actions", "AppPaths", "APP_NAME"]


# set app name
APP_NAME: LiteralString = "Trimshh"
AUTHOR: LiteralString = "Wenyang Tai"
COMPANY: LiteralString = "WENAN"
APP_VERSION: LiteralString = "0.1.0"
ADDRESS: LiteralString = (
    "6F.-1, No. 442, Changchun Rd., Songshan Dist., Taipei City 105, Taiwan (R.O.C.)"
)


class CONTACT_INFO(StrEnum):
    EMAIL = "superyngo@gmail.com"


class Actions(StrEnum):
    """_summary_

    Args:
        StrEnum (_type_): _description_
    """

    CONVERTER = auto()
    SPEEDUP = auto()
    UPLOADER = auto()


# Get the parent directory of the current app
runtime_pth = Path(os.path.abspath(sys.argv[0])).parent


# set app base path
class AppPaths(PathEnum):
    USERPROFILE = Path(os.environ["USERPROFILE"])
    RUNTIME_PATH = runtime_pth
    BIN = RUNTIME_PATH / "bin"
    PROGRAM_DATA = Path(os.environ["PROGRAMDATA"]) / APP_NAME  # C:\ProgramData
    APP_DATA = Path(os.environ["APPDATA"]) / APP_NAME  # C:\Users\user\AppData\Roaming
    CONFIG = APP_DATA / "config.conf"
    LOGS = APP_DATA / "Logs"
