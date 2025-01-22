from pathlib import Path
from .logger_module import setup_logger, Logger
from ...config import config

logger: Logger = setup_logger(
    config.AppPaths.LOGS, config.AppPaths.RUNTIME_PATH / "config" / "logger.conf"
)

__all__: list[str] = ["logger"]
