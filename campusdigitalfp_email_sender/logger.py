import logging
import sys
from pathlib import Path

LOG_FILE = "campusdigitalfp_email_sender.log"
FMT = "%(asctime)s [%(levelname)s] %(message)s"


def setup_logger(level: str = "INFO", log_file: str = LOG_FILE) -> logging.Logger:
    """Devuelve logger ya configurado para consola + fichero."""
    logger = logging.getLogger("email_sender")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # no duplicar handlers en sucesivas llamadas (utiles en tests)
    if logger.handlers:
        return logger

    # consola
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(FMT))
    logger.addHandler(console)

    # fichero
    file_h = logging.FileHandler(log_file, encoding="utf-8")
    file_h.setFormatter(logging.Formatter(FMT))
    logger.addHandler(file_h)

    return logger