import contextlib
import logging
import sys
from typing import Generator


class StreamToLogger:
    """Fake file-like stream object that redirects writes to a logger instance."""

    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        """Initialize the stream-to-logger adapter.

        Args:
            logger: Target logger instance.
            level: Log level for messages.
        """
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf: str) -> None:
        """Write buffer to logger, line by line."""
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self) -> None:
        """Flush the stream (no-op for logger)."""
        pass


@contextlib.contextmanager
def redirect_stdout_to_logger(
    logger: logging.Logger, level: int = logging.INFO
) -> Generator[None, None, None]:
    """Context manager to redirect stdout to a logger."""
    original_stdout = sys.stdout
    sys.stdout = StreamToLogger(logger, level)  # type: ignore
    try:
        yield
    finally:
        sys.stdout = original_stdout
