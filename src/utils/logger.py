"""Structured logging helpers used by the FastAPI application.

Data flow:
    Startup code calls :func:`configure_logger` once to initialize stdlib
    logging + structlog processors. Runtime modules then request contextual
    loggers through :func:`get_logger` and emit JSON logs for observability.
"""

import logging

import structlog


def configure_logger(level: str = "INFO") -> None:
    """Configure process-wide logging behavior.

    Args:
        level: Log level name such as ``"INFO"`` or ``"DEBUG"``.

    Data flow:
        1. Resolve the level into a stdlib logging constant.
        2. Configure root logging output format.
        3. Configure structlog processors so all emitted events become
           JSON records with timestamp and level metadata.
    """
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


def get_logger(name: str):
    """Return a structlog logger scoped to a module or component.

    Args:
        name: Logger namespace, usually ``__name__``.

    Returns:
        A configured structlog logger instance.
    """
    return structlog.get_logger(name)
