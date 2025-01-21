from typing import TypedDict, NotRequired
from pathlib import Path
from enum import StrEnum, auto


class CutSlConfig(TypedDict):
    dB: NotRequired[int]
    sl_duration: NotRequired[float]
    seg_min_duration: NotRequired[float]


class MideoMergerTask(TypedDict):
    folder_path: Path
    start_hour: int
    delete_after: bool
    valid_extensions: NotRequired[set[str]]


# SpeedupTask
class CutSlSpeedupTask(TypedDict):
    folder_path: Path
    multiple: int | float
    same_encode: NotRequired[bool]
    valid_extensions: NotRequired[set[str]]
    cut_sl_config: NotRequired[CutSlConfig]


class VideoSuffix(StrEnum):
    MP4 = auto()
    MKV = auto()
    AVI = auto()
