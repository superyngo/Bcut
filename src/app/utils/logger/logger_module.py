import logging
from logging import config as LoggerConfig, Logger
import os
from datetime import datetime
import configparser
from pathlib import Path


# Multiton state
_instances: dict[Path, Logger] = {}


def setup_logger(
    log_path: Path | None = None, config_path: Path | None = None
) -> Logger:

    # Ensure the log directory exists in the executing root
    if log_path is None:
        log_path = Path.cwd()
    if log_path in _instances:
        return _instances[log_path]
    log_path.mkdir(parents=True, exist_ok=True)

    if config_path is None:
        # Determine the path to the logger module
        module_path: Path = Path(__file__).parent
        # Construct the path to the configuration file within the package's config folder
        config_path = module_path / "config" / "logger.conf"

    # Check if the configuration file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' does not exist.")

    # Load the configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Get the current date for the log filename
    datestamp: str = datetime.now().strftime("%Y-%m-%d")
    log_filename: Path = log_path / f"{datestamp}.log"

    # Update the file handler's filename in the configuration
    config.set("handler_fileHandler", "args", f"(r'{log_filename}', 'a')")

    # Apply the logging configuration
    LoggerConfig.fileConfig(config)

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
