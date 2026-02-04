import logging
from logging.handlers import RotatingFileHandler
import os
from colorlog import ColoredFormatter
import sys
from typing import Any, cast

# --- Directories ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "netmon.log")

SUCCESS = 50
logging.addLevelName(SUCCESS, "SUCCESS")


class NetmonLogger(logging.Logger):
    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, message, args, **kwargs)


logging.setLoggerClass(NetmonLogger)

# --- Logger ---
logger = cast(NetmonLogger, logging.getLogger("netmon"))
logger.setLevel(SUCCESS)  # base level, log everything in file

# --- File Handler (everything) ---
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)  # log everything to file
logger.addHandler(file_handler)

# --- Console Handler (only SUCCESS) ---
console_handler = logging.StreamHandler(sys.stdout)
console_formatter = ColoredFormatter(
    "%(log_color)s%(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "blue",
        "SUCCESS": "green",
        "WARNING": "yellow",
        "ERROR": "red",
    },
)
if sys.platform.startswith("win"):
    os.system("chcp 65001")
console_handler.setFormatter(console_formatter)
console_handler.setLevel(SUCCESS)  # only show SUCCESS in console
logger.addHandler(console_handler)

# --- Optional helper functions ---
def info(msg: str):
    logger.info(msg)

def warning(msg: str):
    logger.warning(msg)

def error(msg: str):
    logger.error(msg)

def debug(msg: str):
    logger.debug(msg)

def log_success(msg: str):
    logger.success(msg)
