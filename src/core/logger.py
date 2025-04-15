import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def logger_init(
    level: str = "DEBUG",
    log_dir: str = "logs",
    log_file_format: str = "{time:YYYY-MM-DD}.log",
    log_file_rotation: str = "100 MB",
    log_file_retention: str = "7 days",
    log_file_compression: Optional[str] = "gz",
) -> None:
    try:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        (log_path / ".gitignore").write_text("*", encoding="utf-8")
    except Exception as e:
        print(f"Failed to initialize log directory: {e}", file=sys.stderr)
        return

    logger.remove()

    # Define log levels with colors
    log_levels = {
        "DEBUG": "<magenta>",
        "INFO": "<green>",
        "SUCCESS": "<cyan>",
        "WARNING": "<yellow>",
        "ERROR": "<red>",
        "CRITICAL": "<bold><red>",
    }
    for level_name, color in log_levels.items():
        logger.level(level_name, color=color)

    logger.add(
        sys.stderr,
        backtrace=True,
        diagnose=True,
        colorize=True,
        level=level,
        format="<level>{level: <8}</level> | <blink><black>{name}:{function}:{line}</black></blink> - <level>{message}</level>",
    )

    logger.add(
        f"{log_dir}/{log_file_format}",
        rotation=log_file_rotation,
        retention=log_file_retention,
        backtrace=True,
        diagnose=True,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level: <8}| {name}:{function}:{line} | {message}",
        compression=log_file_compression,
    )
