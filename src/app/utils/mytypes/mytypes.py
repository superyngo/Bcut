from enum import ReprEnum
from pathlib import Path
from typing import TypedDict, NotRequired


class PathEnum(Path, ReprEnum):
    """
    Enum where members are also (and must be) Path objects
    """

    def __new__(cls, *values):
        # values must already be of type `Path` or `str`
        if len(values) != 1:
            raise TypeError("PathEnum requires exactly one argument")
        if not isinstance(values[0], (str, Path)):
            raise TypeError("%r is not a valid path or string" % (values[0],))
        value = Path(values[0])
        member = Path.__new__(cls, value)
        member._value_ = value
        return member

    def __getattr__(self, name):
        """
        Directly refer to the attribute's value.
        """
        return getattr(self._value_, name)

    def __truediv__(self, other):
        # Allow path operations directly on the enum member
        return self._value_ / other


__all__: list[str] = ["PathEnum"]
