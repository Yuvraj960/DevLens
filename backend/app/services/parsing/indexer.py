from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Import, Symbol
from app.services.parsing.manager import language_manager


class SymbolIndexer:
    @staticmethod
    async def index_file(
        session: AsyncSession,
        file_model: File,
        file_content: str,
    ) -> int:
        """Parses a single file content and persists extracted symbols & imports."""
        # Always clean existing symbols/imports first (handles re-ingestion and zero-symbol edits)
        del_sym = select(Symbol).where(Symbol.file_id == file_model.id)
        existing_syms = (await session.execute(del_sym)).scalars().all()
        for s in existing_syms:
            await session.delete(s)

        del_imp = select(Import).where(Import.file_id == file_model.id)
        existing_imps = (await session.execute(del_imp)).scalars().all()
        for i in existing_imps:
            await session.delete(i)

        # Run Language Manager parser
        parse_res = language_manager.parse_content(
            file_path=file_model.path,
            language=file_model.language,
            content=file_content,
        )

        if not parse_res.symbols and not parse_res.imports:
            return 0

        # Insert new symbols
        symbol_models = [
            Symbol(
                file_id=file_model.id,
                name=sym.name,
                kind=sym.kind,
                signature=sym.signature,
                docstring=sym.docstring,
                start_line=sym.start_line,
                end_line=sym.end_line,
                is_exported=sym.is_exported,
                is_async=sym.is_async,
            )
            for sym in parse_res.symbols
        ]
        session.add_all(symbol_models)

        # Insert new imports
        import_models = [
            Import(
                file_id=file_model.id,
                source=imp.source,
                imported_symbol=imp.imported_symbol,
                is_external=imp.is_external,
            )
            for imp in parse_res.imports
        ]
        session.add_all(import_models)

        file_model.parsed_at = datetime.now(timezone.utc)

        return len(symbol_models)
