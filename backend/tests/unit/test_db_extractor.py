import pytest
from app.models import File, Symbol
from app.services.discovery.db_extractor import DbExtractor


@pytest.mark.asyncio
async def test_db_extractor(db_session):
    model_file = File(path="app/models/user.py", language="python", size_bytes=150, loc=20, content_hash="hd1")
    db_session.add(model_file)
    await db_session.flush()

    sym = Symbol(
        file_id=model_file.id,
        name="User",
        kind="class",
        signature="class User(Base)",
        start_line=5,
        end_line=20,
    )
    db_session.add(sym)
    await db_session.commit()

    schema = await DbExtractor.extract_database_schema(db_session, "test_repo_id", [model_file])

    assert "tables" in schema
    assert "metadata" in schema
    assert schema["metadata"]["total_tables"] >= 1
    table_names = [t["name"] for t in schema["tables"]]
    assert "users" in table_names
