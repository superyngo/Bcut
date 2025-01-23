import os
from pathlib import Path
from .ffmpeg_converter import (
    speedup,
    jumpcut,
    convert,
    cut,
    merge,
    probe_encoding_info,
    probe_duration,
    is_valid_video,
    detect_non_silence,
    cut_silence,
    cut_silence_rerender,
)
from . import types

PACKAGE_NAME = "ffmpeg_converter"

# Set custom paths for ffmpeg and ffprobe executables
# Get the absolute path of the current file
current_file_path = Path(__file__).resolve()

# Set the ./bin path to the PATH environment variable
bin_path = current_file_path.parent / "bin"
os.environ["PATH"] = a = str(bin_path) + os.pathsep + os.environ["PATH"]


class ffmpeg_Error(Exception):
    def __init__(self, cmd, stdout, stderr):
        super(Error, self).__init__(
            "{} error (see stderr output for detail)".format(cmd)
        )
        self.stdout = stdout
        self.stderr = stderr


__all__: list[str] = [
    "speedup",
    "jumpcut",
    "convert",
    "cut",
    "merge",
    "probe_encoding_info",
    "probe_duration",
    "is_valid_video",
    "detect_non_silence",
    "cut_silence",
    "cut_silence_rerender",
    "ffmpeg_Error",
    "types",
]
