from logging import Logger
import os
import app.common.constants as constants
import app.common.mytypes as mytypes
from app.common.logger import setup_logger

# Create App directories if they don't exist
constants.AppPaths.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
constants.AppPaths.APP_DATA.mkdir(parents=True, exist_ok=True)
# Create logger
logger: Logger = setup_logger(constants.AppPaths.LOGS)

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""
os.environ["PYTHONUTF8"] = "1"

__all__: list[str] = ["constants", "mytypes", "logger"]
