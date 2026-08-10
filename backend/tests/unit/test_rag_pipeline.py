import pytest
from app.services.chat.context_assembler import ContextAssembler
from app.services.chat.query_expander import QueryExpander


def test_query_expander():
    expanded = QueryExpander.expand_query("Where is JWT user authentication verified in this repo?")
    assert expanded["original_query"] == "Where is JWT user authentication verified in this repo?"
    assert "jwt" in expanded["keywords"]
    assert len(expanded["search_queries"]) >= 1


def test_context_assembler():
    contexts = [
        {
            "symbol_id": "123",
            "name": "verifyJwt",
            "kind": "function",
            "file_path": "src/auth/jwt.ts",
            "start_line": 10,
            "end_line": 25,
            "snippet": "export function verifyJwt(token: string) {}",
        }
    ]
    assembled = ContextAssembler.assemble_prompt_context(contexts)
    assert "[[src/auth/jwt.ts:10-25]]" in assembled
    assert "verifyJwt" in assembled
