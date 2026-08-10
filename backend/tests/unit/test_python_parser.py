from app.services.parsing.parsers.python import PythonParser


def test_python_parser_functions_classes_imports():
    code = """import os
from typing import List

class BaseManager:
    \"\"\"Base manager docstring\"\"\"
    def __init__(self):
        pass

async def process_batch(items: List[str]):
    \"\"\"Process batch items asynchronously\"\"\"
    return len(items)
"""
    parser = PythonParser()
    res = parser.parse("app/services.py", code)

    assert len(res.symbols) == 3  # BaseManager, __init__, process_batch

    # Check class
    cls_sym = next(s for s in res.symbols if s.name == "BaseManager")
    assert cls_sym.kind == "class"
    assert cls_sym.docstring == "BaseManager docstring"

    # Check async function
    fn_sym = next(s for s in res.symbols if s.name == "process_batch")
    assert fn_sym.kind == "function"
    assert fn_sym.is_async is True
    assert fn_sym.docstring == "Process batch items asynchronously"

    # Check imports
    assert len(res.imports) == 2
    assert any(i.source == "os" for i in res.imports)
    assert any(i.source == "typing" and i.imported_symbol == "List" for i in res.imports)
