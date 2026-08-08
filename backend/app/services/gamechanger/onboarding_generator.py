from typing import Any
from app.models import File


class OnboardingGenerator:
    """Topological developer onboarding path generator."""

    @classmethod
    def generate_onboarding_path(
        cls,
        files: list[File],
    ) -> list[dict[str, Any]]:
        steps = [
            {
                "step": 1,
                "title": "Core Domain Models & Database Schemas",
                "estimated_minutes": 8,
                "description": "Understand core database entities (Repo, File, Symbol, Import, Job, RepoAnalysis).",
                "key_files": ["backend/app/models/repo.py", "backend/app/models/symbol.py"],
                "checkpoint_question": "What is the relation between Repo and File entities?",
            },
            {
                "step": 2,
                "title": "Ingestion & Multi-Language AST Parsing Core",
                "estimated_minutes": 10,
                "description": "Examine Tree-sitter parsers (TSParser, PythonParser, GoParser) and Qdrant vector chunking.",
                "key_files": ["backend/app/services/ingestion.py", "backend/app/services/parsing/ts_parser.py"],
                "checkpoint_question": "How does content-hash deduplication work?",
            },
            {
                "step": 3,
                "title": "Grounded RAG & Structural Query DSL Engine",
                "estimated_minutes": 7,
                "description": "Study 4-stage LangGraph grounded RAG pipeline and DSL parser.",
                "key_files": ["backend/app/services/chat/service.py", "backend/app/services/search/dsl_parser.py"],
                "checkpoint_question": "What syntax rule forces AI grounding?",
            },
            {
                "step": 4,
                "title": "Flagship Multi-Tier Execution Trace Canvas",
                "estimated_minutes": 5,
                "description": "Explore end-to-end call graph traversal and confidence edge scoring.",
                "key_files": ["backend/app/services/trace/engine.py", "frontend/src/components/trace/FlagshipTraceCanvas.tsx"],
                "checkpoint_question": "What distinguishes solid vs dashed trace edges?",
            },
        ]
        return steps
