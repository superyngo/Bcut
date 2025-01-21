import logging
from logging import config as LoggerConfig, Logger
import os
from datetime import datetime
import configparser
from pathlib import Path


# Determine the path to the logger module
_module_path: Path = Path(__file__).parent

# Construct the path to the configuration file within the package's config folder
_config_path: Path = _module_path / "config" / "logger.conf"

# Multiton state
_instances: dict[Path, Logger] = {}


def setup_logger(log_path: Path | None = None) -> Logger:

    # Ensure the log directory exists in the executing root
    log_directory: Path = log_path or Path.cwd() / "Logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    if log_path in _instances:
        return _instances[log_directory]

    # Check if the configuration file exists
    if not os.path.exists(_config_path):
        raise FileNotFoundError(f"Configuration file '{_config_path}' does not exist.")

    # Load the configuration file
    config = configparser.ConfigParser()
    config.read(_config_path)

    # Get the current date for the log filename
    datestamp: str = datetime.now().strftime("%Y-%m-%d")
    log_filename: Path = log_directory / f"{datestamp}.log"

    # Update the file handler's filename in the configuration
    config.set("handler_fileHandler", "args", f"(r'{log_filename}', 'a')")

    # Apply the logging configuration
    LoggerConfig.fileConfig(config)

    # Return the root logger
    _instances[log_directory] = logging.getLogger()
    return _instances[log_directory]


# Example usage
if __name__ == "__main__":
    # logger.debug('This is a debug message')
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
