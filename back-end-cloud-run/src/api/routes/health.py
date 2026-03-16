"""Health-check endpoint definitions."""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Return liveness signal and current UTC timestamp.

    Returns:
        Dictionary with ``status`` and ``timestamp`` keys.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
