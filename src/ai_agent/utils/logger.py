import logging
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str, level: str = "INFO", console: Optional[Console] = None
) -> logging.Logger:
    """Setup a rich logger."""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create rich handler
    handler = RichHandler(
        console=console or Console(),
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
    )

    # Set format
    formatter = logging.Formatter(fmt="%(message)s", datefmt="[%X]")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
