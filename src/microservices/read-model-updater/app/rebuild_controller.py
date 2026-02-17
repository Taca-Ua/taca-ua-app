"""
Rebuild Controller - HTTP endpoints for projection rebuild.

This module provides:
- POST /internal/rebuild - Trigger projection rebuild
- GET /internal/rebuild/status - Check rebuild status

Security:
- Protected by X-INTERNAL-TOKEN header
- Should NOT be exposed via API Gateway
- Only accessible within Docker network
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .config import Config
from .database import get_db_session
from .events import rabbitmq_service
from .logger import logger
from .rebuild_service import RebuildService

router = APIRouter(prefix="/internal", tags=["internal"])


def verify_internal_token(x_internal_token: str = Header(...)) -> bool:
    """
    Verify internal API token.

    This ensures that only authorized internal services can trigger rebuilds.

    Args:
        x_internal_token: Token from X-INTERNAL-TOKEN header

    Returns:
        True if token is valid

    Raises:
        HTTPException: If token is invalid or missing
    """
    if x_internal_token != Config.INTERNAL_API_TOKEN:
        logger.warning(
            "rebuild_unauthorized_attempt",
            message="Invalid internal token provided",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal token",
        )
    return True


@router.post("/rebuild")
async def trigger_rebuild(
    db: Session = Depends(get_db_session),
    _: bool = Depends(verify_internal_token),
):
    """
    Trigger projection rebuild from domain service snapshots.

    This endpoint orchestrates the complete rebuild process:
    1. Pauses event consumption
    2. Clears all projection tables
    3. Fetches snapshots from all domain services
    4. Rebuilds projections from snapshots
    5. Resumes event consumption

    Security:
    - Requires X-INTERNAL-TOKEN header
    - Should only be called by authorized internal tools/services

    **IMPORTANT**: This is a DESTRUCTIVE operation. All projection data
    will be cleared and rebuilt from scratch. Use with caution.

    Returns:
        JSON response with rebuild result including:
        - success: Whether rebuild succeeded
        - message: Human-readable status message
        - records_processed: Number of records inserted
        - duration_seconds: How long rebuild took
        - errors: List of any errors encountered
    """
    logger.info(
        "rebuild_triggered",
        message="Rebuild request received via HTTP endpoint",
    )

    try:
        # Initialize rebuild service
        rebuild_service = RebuildService(
            db_session=db,
            rabbitmq_service=rabbitmq_service,
        )

        # Execute rebuild
        result = await rebuild_service.execute_rebuild()

        # Return appropriate HTTP status code based on result
        if result.success:
            return {
                "success": result.success,
                "message": result.message,
                "records_processed": result.records_processed,
                "duration_seconds": result.duration_seconds,
            }
        else:
            # Rebuild failed but service recovered
            # Return 500 with error details
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": result.success,
                    "message": result.message,
                    "errors": result.errors,
                    "duration_seconds": result.duration_seconds,
                },
            )

    except Exception as e:
        # Unexpected error during rebuild
        logger.error(
            "rebuild_endpoint_error",
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rebuild failed with unexpected error: {str(e)}",
        )


@router.get("/rebuild/status")
async def get_rebuild_status(
    db: Session = Depends(get_db_session),
    _: bool = Depends(verify_internal_token),
):
    """
    Get current rebuild status and projection statistics.

    This endpoint provides information about:
    - Number of records in each projection table
    - Whether event consumption is paused
    - Current state of the read models

    Security:
    - Requires X-INTERNAL-TOKEN header

    Returns:
        JSON response with current status
    """
    logger.info("rebuild_status_requested")

    try:
        rebuild_service = RebuildService(
            db_session=db,
            rabbitmq_service=rabbitmq_service,
        )

        status_info = rebuild_service.get_rebuild_status()

        return {
            "success": True,
            "status": status_info,
        }

    except Exception as e:
        logger.error("rebuild_status_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {str(e)}",
        )


@router.post("/rebuild/pause")
async def pause_event_consumption(
    _: bool = Depends(verify_internal_token),
):
    """
    Manually pause event consumption.

    This can be useful for maintenance or manual intervention.

    Security:
    - Requires X-INTERNAL-TOKEN header

    Returns:
        JSON response confirming pause
    """
    logger.info("event_consumption_pause_requested")

    try:
        rebuild_service = RebuildService(
            db_session=None,  # Not needed for just pausing
            rabbitmq_service=rabbitmq_service,
        )

        await rebuild_service.pause_event_consumption()

        return {
            "success": True,
            "message": "Event consumption paused",
            "paused": rabbitmq_service.is_paused(),
        }

    except Exception as e:
        logger.error("event_consumption_pause_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause event consumption: {str(e)}",
        )


@router.post("/rebuild/resume")
async def resume_event_consumption(
    _: bool = Depends(verify_internal_token),
):
    """
    Manually resume event consumption.

    This resumes processing after a manual pause.

    Security:
    - Requires X-INTERNAL-TOKEN header

    Returns:
        JSON response confirming resume
    """
    logger.info("event_consumption_resume_requested")

    try:
        rebuild_service = RebuildService(
            db_session=None,  # Not needed for just resuming
            rabbitmq_service=rabbitmq_service,
        )

        await rebuild_service.resume_event_consumption()

        return {
            "success": True,
            "message": "Event consumption resumed",
            "paused": rabbitmq_service.is_paused(),
        }

    except Exception as e:
        logger.error("event_consumption_resume_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume event consumption: {str(e)}",
        )
