from app.services.parsing.base import SymbolData
from app.services.search.vector_indexer import VectorIndexer


def test_ast_symbol_chunking():
    content = """
function calculateTotal(items: any[]): number {
    return items.reduce((acc, item) => acc + item.price, 0);
}

class InvoiceProcessor {
    process() {
        console.log('processing');
    }
}
"""
    symbols = [
        SymbolData(name="calculateTotal", kind="function", start_line=2, end_line=4),
        SymbolData(name="InvoiceProcessor", kind="class", start_line=6, end_line=10),
    ]

    chunks = VectorIndexer.chunk_file_by_symbols(
        repo_id="test_repo",
        file_path="src/invoice.ts",
        language="typescript",
        content=content,
        symbols=symbols,
    )

    assert len(chunks) >= 2
    sym_chunk = next(c for c in chunks if c.symbol_name == "calculateTotal")
    assert "calculateTotal" in sym_chunk.text
    assert sym_chunk.kind == "function"
