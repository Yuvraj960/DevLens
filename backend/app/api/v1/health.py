from fastapi import APIRouter
from app.schemas.common import MessageResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=MessageResponse)
async def health_check() -> MessageResponse:
    return MessageResponse(message="DevLens Backend Service Healthy")
