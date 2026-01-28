"""
Structured logging configuration for cloud-native environments.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Perfect for cloud-native environments and log aggregation tools.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Standard logging attributes to exclude from extra fields
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_info",
            "exc_text",
            "stack_info",
            "getMessage",
            "asctime",
        }

        # Add all extra fields from the record (anything not in standard attributes)
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                # Rename 'duration' to 'duration_seconds' for clarity
                if key == "duration":
                    log_data["duration_seconds"] = value
                else:
                    log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data)


def setup_logger(name: str = "fastapi_app") -> logging.Logger:
    """
    Setup and configure structured logger.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    # Get configuration from environment
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

    # Setup structured logging
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(log_level)
    logger.propagate = False  # Don't pass to root logger

    return logger


# Create global logger instance
logger = setup_logger()
