import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.chat.service import ChatService

router = APIRouter(prefix="/repos/{repo_id}", tags=["Chat"])


class ChatRequestPayload(BaseModel):
    message: str = Field(..., max_length=4000)
    conversation_id: str | None = None
    stream: bool = False


@router.post(
    "/chat",
    response_model=dict[str, Any],
    summary="Ground-based RAG chat",
    description="RAG chat grounded strictly in repository context with file:line citations.",
)
async def chat_with_codebase(
    repo_id: uuid.UUID,
    payload: ChatRequestPayload,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    conv_uuid = None
    if payload.conversation_id:
        try:
            conv_uuid = uuid.UUID(payload.conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid conversation_id: '{payload.conversation_id}' is not a valid UUID.",
            )

    response = await ChatService.process_chat(
        session=db,
        repo_id=repo_id,
        user_message=payload.message,
        conversation_id=conv_uuid,
    )
    return response
