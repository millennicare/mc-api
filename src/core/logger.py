import logging
import sys


def setup_logger(name: str = "app") -> logging.Logger:
    """
    Set up and return a configured logger instance.
    Can be called multiple times but will only configure once.
    """
    logger = logging.getLogger(name)

    # Only add handlers if the logger hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
