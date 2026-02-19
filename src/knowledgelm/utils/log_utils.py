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
        temp_linebuf = self.linebuf + buf
        self.linebuf = ""
        for line in temp_linebuf.splitlines(keepends=True):
            if line.endswith('\n'):
                self.logger.log(self.level, line.rstrip())
            else:
                self.linebuf += line

    def flush(self) -> None:
        """Flush the stream."""
        if self.linebuf:
            self.logger.log(self.level, self.linebuf.rstrip())
            self.linebuf = ""


@contextlib.contextmanager
def redirect_output_to_logger(
    logger: logging.Logger, level: int = logging.INFO
) -> Generator[None, None, None]:
    """Context manager to redirect stdout and stderr to a logger."""
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    sys.stdout = StreamToLogger(logger, level)  # type: ignore
    sys.stderr = StreamToLogger(logger, level)  # type: ignore
    try:
        yield
    finally:
        # Flush any remaining buffer before restoring
        if isinstance(sys.stdout, StreamToLogger):
            sys.stdout.flush()
        if isinstance(sys.stderr, StreamToLogger):
            sys.stderr.flush()

        sys.stdout = original_stdout
        sys.stderr = original_stderr

# Alias for backward compatibility
redirect_stdout_to_logger = redirect_output_to_logger
