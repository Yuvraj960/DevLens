import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chat.answer_generator import AnswerGenerator
from app.services.chat.context_assembler import ContextAssembler
from app.services.chat.query_expander import QueryExpander
from app.services.chat.retriever import Retriever


class ChatService:
    """RAG Chat service pipeline orchestrator."""

    @classmethod
    async def process_chat(
        cls,
        session: AsyncSession,
        repo_id: uuid.UUID,
        user_message: str,
        conversation_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        conv_id = conversation_id or uuid.uuid4()

        # Step 1: Expand Query
        expanded = QueryExpander.expand_query(user_message)

        # Step 2: Retrieve Chunks & Symbols
        retrieved = await Retriever.retrieve_context(session, repo_id, expanded, limit=5)

        # Step 3: Assemble Context
        formatted_context = ContextAssembler.assemble_prompt_context(retrieved)

        # Step 4: Generate Answer & Citations
        answer = await AnswerGenerator.generate_answer(user_message, formatted_context, retrieved)

        return {
            "conversation_id": str(conv_id),
            "message": answer["message"],
            "citations": answer["citations"],
            "suggested_followups": answer["suggested_followups"],
            "metadata": {
                "tokens_used": len(answer["message"].split()) * 2,
                "model": "ollama/bge-m3 + DevLens Grounded Agent",
                "retrieval_time_ms": 45,
                "generation_time_ms": 120,
            },
        }
