from typing import TypedDict, NotRequired
from pathlib import Path
from ..actions.mideo_converter.types import (
    MideoMergerTask,
    CutSlSpeedupTask,
)

# from ..actions.GPhoto_uploader.types import UploaderTask


# class CsBasicComponent:
#     def __getattr__(self, name):
#         raise AttributeError(f"'{self.__class__.__name__}' '{name}' was not set")


# class MyDataclass:
#     def __init__(self, **kwargs) -> None:
#         for key, value in kwargs.items():
#             if key in self.__slots__:
#                 setattr(self, key, value)
#             else:
#                 raise AttributeError(
#                     f"'{key}' is not a valid attribute for {self.__class__.__name__}"
#                 )

#     def __getattr__(self, name):
#         if name in self.__slots__:
#             raise AttributeError(f"'{name}' was not set during initialization")
#         raise AttributeError(
#             f"'{self.__class__.__name__}' object has no attribute '{name}'"
#         )


# Actions
class AssignmentInfo(TypedDict):
    filename: Path
    selected: NotRequired[set[int]]


class SpeedupInfo(AssignmentInfo):
    assignments: list[CutSlSpeedupTask]


class MideoMergerInfo(AssignmentInfo):
    assignments: list[MideoMergerTask]


# class UploaderInfo(AssignmentInfo):
#     assignments: list[UploaderTask]
