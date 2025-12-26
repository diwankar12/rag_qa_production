from functools import lru_cache
import logging


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application.
     
    Args:
        log_level (str): The logging level to set for the application.
        Valid values are "DEBUG", "INFO", "WARNING", "ERROR", and "CRITICAL".
        Default is "INFO".
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S')
    
    # set up root logger 
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    #remove existing handlers 
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # set up stream handler 
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def setup_log(log_level: str = "INFO") -> None:
    """Backwards-compatible alias for setup_logging()."""
    setup_logging(log_level)


@lru_cache
def get_logger(name : str) -> logging.Logger:
    """Get the root logger configured for the application.
    
    Returns:
        logging.Logger: The root logger.
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capability to classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)
        
