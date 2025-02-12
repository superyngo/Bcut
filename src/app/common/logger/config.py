from typing import Any

logging_config: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "root": {"level": "INFO", "handlers": ["consoleHandler", "fileHandler"]}
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "formatter",
            "stream": "ext://sys.stdout",
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "formatter",
            "filename": "app.log",
        },
    },
    "formatters": {
        # "formatter": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        "formatter": {"format": "%(asctime)s - %(levelname)s - %(message)s"}
    },
}
