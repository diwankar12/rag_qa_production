
from app.utils.logger import get_logger
from fastapi import APIRouter, HTTPException
from app.api.schemas import HealthResponse, ReadinessResponse
from app import __version__
from datetime import datetime
from app.core.vector_store import VectorStoreService

logger= get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("",
            summary="Health Check",
            description="Check the health status of the application.",
            response_model=HealthResponse
            )

async def health_check() -> HealthResponse:
    """Health check endpoint to verify if the application is running."""
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=__version__,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description="Checks if the service is ready to handle requests (including DB connectivity).",
)
async def readiness_check() -> ReadinessResponse:
    """Readiness check endpoint to verify if the application is ready."""

    logger.debug("Readiness check requested")
    # Here you would typically check database connectivity and other dependencies
    try:
        vector_store = VectorStoreService()
        is_healthy = vector_store.health_check()

        if not is_healthy:
                raise HTTPException(
                    status_code=503,
                    detail="Vector store is not healthy",
                )

        collection_info = vector_store.get_collection_info()

        return ReadinessResponse(
                status="ready",
                qdrant_connected=True,
                collection_info=collection_info,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}",
        )