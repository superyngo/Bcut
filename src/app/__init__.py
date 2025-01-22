from .config import config

# Create App directories if they don't exist
config.AppPaths.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
config.AppPaths.APP_DATA.mkdir(parents=True, exist_ok=True)

from .actions import mideo_converter  # , GPhoto_uploader
from . import utils
from .utils import logger
from .models import tasks

# from .services.my_driver import browser_instances
from .services import ffmpeg_converter

# from .actions.GPhoto_uploader.gp_uploader import upload_handler


__all__: list[str] = [
    "config",
    "utils",
    "logger",
    "mideo_converter",
    # "GPhoto_uploader",
    "tasks",
    # "browser_instances",
    "ffmpeg_converter",
]
