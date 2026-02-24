from fastapi import FastAPI
from datetime import datetime
from .models import HealthCheckResponse, HealthStatus

app = FastAPI(
    title="Template Service",
    description="Template service for enhancia-3",
    version="0.1.0",
)

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint that returns service status."""
    return HealthCheckResponse(
        status=HealthStatus.HEALTHY,
        message="Service is running normally",
        timestamp=datetime.now().isoformat()
    )