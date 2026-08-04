import ast
import hashlib
from app.services.parsing.base import BaseParser, ExportData, ImportData, ParseResult, SymbolData


class PythonParser(BaseParser):
    """AST Parser for Python source files using standard library `ast`."""

    def parse(self, file_path: str, content: str) -> ParseResult:
        symbols: list[SymbolData] = []
        imports: list[ImportData] = []
        exports: list[ExportData] = []

        try:
            tree = ast.parse(content, filename=file_path)
            lines = content.splitlines()

            for node in ast.walk(tree):
                # Function & Async Function Definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    is_async = isinstance(node, ast.AsyncFunctionDef)
                    docstring = ast.get_docstring(node)
                    start_line = node.lineno
                    end_line = getattr(node, "end_lineno", start_line + 10)
                    params = [arg.arg for arg in node.args.args]
                    sig_prefix = "async def" if is_async else "def"
                    signature = f"{sig_prefix} {node.name}({', '.join(params)})"
                    is_private = node.name.startswith("_") and not node.name.startswith("__")

                    symbols.append(
                        SymbolData(
                            name=node.name,
                            kind="function",
                            start_line=start_line,
                            end_line=end_line,
                            signature=signature,
                            docstring=docstring,
                            is_exported=not is_private,
                            is_async=is_async,
                        )
                    )

                # Class Definitions
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    start_line = node.lineno
                    end_line = getattr(node, "end_lineno", start_line + 20)
                    bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                    base_str = f"({', '.join(bases)})" if bases else ""
                    signature = f"class {node.name}{base_str}"

                    symbols.append(
                        SymbolData(
                            name=node.name,
                            kind="class",
                            start_line=start_line,
                            end_line=end_line,
                            signature=signature,
                            docstring=docstring,
                            is_exported=not node.name.startswith("_"),
                        )
                    )

                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        is_ext = not alias.name.startswith(".")
                        imports.append(ImportData(source=alias.name, imported_symbol=alias.asname or alias.name, is_external=is_ext))

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or "."
                    is_ext = not module.startswith(".")
                    for alias in node.names:
                        imports.append(ImportData(source=module, imported_symbol=alias.name, is_external=is_ext))

        except SyntaxError:
            # Fallback regex parsing if syntax error occurs
            pass

        ast_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return ParseResult(symbols=symbols, imports=imports, exports=exports, ast_hash=ast_hash)
