import logging
from logging import config as LoggerConfig
import os, sys
from datetime import datetime
import configparser
from pathlib import Path
from .config import logging_config

runtime_pth = Path(os.path.abspath(sys.argv[0])).parent
# Get the current date for the log filename
datestamp: str = datetime.now().strftime("%Y-%m-%d")

# Multiton state
_instances: dict[Path, logging.Logger] = {}


def setup_logger(
    log_path: Path | None = None, config_path: Path | None = None
) -> logging.Logger:

    # Ensure the log directory exists in the executing root
    if log_path is None:
        log_path = runtime_pth / "Logs"
    if log_path in _instances:
        return _instances[log_path]
    log_path.mkdir(parents=True, exist_ok=True)
    log_filename: Path = log_path / f"{datestamp}.log"
    print(f"{log_filename = }")

    if config_path is None:
        config_path = Path()

    # Check if the configuration file exists or roll back to the default configuration
    if config_path.is_file():
        # Load the configuration file
        config = configparser.ConfigParser()
        config.read(config_path)
        # Update the file handler's filename in the configuration
        config.set("handler_fileHandler", "args", f"(r'{log_filename}', 'a')")
        # Apply the logging configuration
        LoggerConfig.fileConfig(config)

    else:
        # Update the file handler's filename in the configuration
        logging_config["handlers"]["fileHandler"]["filename"] = log_filename
        # Apply the logging configuration
        LoggerConfig.dictConfig(logging_config)

    # Return the root logger
    _instances[log_path] = logging.getLogger()

    return _instances[log_path]


# Example usage
if __name__ == "__main__":
    logger: Logger = setup_logger()
    # logger.debug('This is a debug message')
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
