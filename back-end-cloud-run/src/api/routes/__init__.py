"""Convenience exports for HTTP route routers.

Data flow:
	`src.main` imports these routers and mounts them on the FastAPI app.
"""

from src.api.routes.generate import router as generate_router
from src.api.routes.health import router as health_router

__all__ = ["generate_router", "health_router"]
