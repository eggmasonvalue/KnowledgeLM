import contextlib
import logging
import sys
from typing import Generator


class StreamToLogger:
    """Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf: str) -> None:
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self) -> None:
        pass


@contextlib.contextmanager
def redirect_stdout_to_logger(
    logger: logging.Logger, level: int = logging.INFO
) -> Generator[None, None, None]:
    """Context manager to redirect stdout to a logger.
    """
    original_stdout = sys.stdout
    sys.stdout = StreamToLogger(logger, level)  # type: ignore
    try:
        yield
    finally:
        sys.stdout = original_stdout
