# from .common import common
from pathlib import Path
from logging import Logger
from .logger_module import setup_logger
from .common import load_assignment
from ...config.app_config import AppPaths

_log_path: Path = AppPaths.LOGS
logger: Logger = setup_logger(_log_path)

__all__: list[str] = ["logger", "load_assignment"]
