from src.config import Settings


def configure_tracing(settings: Settings) -> None:
    # Placeholder hook for Cloud Trace wiring with OpenTelemetry.
    # Left intentionally lightweight for fast local startup.
    if settings.enable_cloud_trace:
        return
