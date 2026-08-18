import logging
import sys
from typing import Optional

def setup_logging(level: Optional[str] = "INFO") -> logging.Logger:
    """
    Configures the root logger with a consistent format and log level.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Returns:
        The configured root logger instance.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
    
    # Suppress noisy third-party logs (optional)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return root_logger

# Global logger instance for convenience
logger = setup_logging()