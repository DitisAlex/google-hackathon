"""Custom API exception types.

Data flow:
    Route handlers raise :class:`ApiError` with domain-specific error codes.
    The global exception handler in ``src.main`` serializes it into the common
    ``{"error": ...}`` response shape.
"""

from fastapi import HTTPException


class ApiError(HTTPException):
    """HTTP exception with a consistent, typed error payload.

    Args:
        status_code: HTTP response code returned to the client.
        code: Stable machine-readable error identifier.
        message: Human-readable error description.
        details: Optional structured metadata for debugging.
    """

    def __init__(self, status_code: int, code: str, message: str, details: dict | None = None) -> None:
        """Build an API error response in the project-standard envelope."""
        super().__init__(status_code=status_code, detail={"error": {"code": code, "message": message, "details": details or {}}})
