import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs as JSON
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logger(name: str = "app") -> logging.Logger:
    """
    Set up and return a configured logger instance with JSON formatting.
    Can be called multiple times but will only configure once.
    """
    logger = logging.getLogger(name)

    # Only add handlers if the logger hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Console Handler with JSON formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JSONFormatter())

        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
