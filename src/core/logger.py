import sys

from pathlib import Path

from loguru import logger


def logger_init(level: str = "DEBUG") -> None:
    Path("logs").mkdir(exist_ok=True)
    Path("logs/.gitignore").write_text("*", encoding="utf-8")

    logger.remove()

    logger.level("DEBUG", color="<magenta>")
    logger.level("INFO", color="<green>")
    logger.level("SUCCESS", color="<cyan>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<red>")
    logger.level("CRITICAL", color="<bold><red>")

    logger.add(
        "logs/{time:YYYY-MM-DD}.log",
        rotation="100 MB",
        retention="7 days",
        backtrace=True,
        diagnose=True,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level: <8}| {name}:{function}:{line} | {message}",
        compression="gz",
    )
    logger.add(
        sys.stderr,
        backtrace=True,
        diagnose=True,
        colorize=True,
        level=level,
        format="<level>{level: <8}</level> | "
        "<blink><black>{name}:{function}:{line}</black></blink> - "
        "<level>{message}</level>",
    )
