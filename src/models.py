from enum import Enum

from pydantic import BaseModel


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: HealthStatus
    message: str
    timestamp: str
    service_name: str = "template-service"