import sys

from loguru import logger

_handlers = []


def configure_logging(path, stage, run_id):
    global _handlers
    for handler in _handlers:
        logger.remove(handler)
    if not _handlers:
        logger.remove()
    fmt = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[stage]} | {extra[run_id]} | {message}"
    logger.configure(extra={"stage": stage, "run_id": run_id})
    _handlers = [
        logger.add(sys.stderr, format=fmt, level="INFO"),
        logger.add(path, format=fmt, encoding="utf-8", level="DEBUG"),
    ]
    return logger


def close_logging():
    global _handlers
    for handler in _handlers:
        logger.remove(handler)
    _handlers = []
