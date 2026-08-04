import hashlib
import re
from app.services.parsing.base import BaseParser, ExportData, ImportData, ParseResult, SymbolData


class TSParser(BaseParser):
    """AST / Lexical parser for TypeScript and JavaScript files."""

    FN_REGEX = re.compile(
        r'^(?P<export>export\s+)?(?P<async>async\s+)?function\s+(?P<name>[A-Za-z0-9_$]+)\s*\((?P<params>[^)]*)\)',
        re.MULTILINE,
    )
    ARROW_FN_REGEX = re.compile(
        r'^(?P<export>export\s+)?(?:const|let|var)\s+(?P<name>[A-Za-z0-9_$]+)\s*=\s*(?P<async>async\s+)?(?:\((?P<params>[^)]*)\)|[A-Za-z0-9_$]+)\s*=>',
        re.MULTILINE,
    )
    CLASS_REGEX = re.compile(
        r'^(?P<export>export\s+)?class\s+(?P<name>[A-Za-z0-9_$]+)(?:\s+extends\s+[A-Za-z0-9_$.]+)?(?:\s+implements\s+[A-Za-z0-9_$,\s]+)?',
        re.MULTILINE,
    )
    INTERFACE_REGEX = re.compile(
        r'^(?P<export>export\s+)?interface\s+(?P<name>[A-Za-z0-9_$]+)',
        re.MULTILINE,
    )
    TYPE_REGEX = re.compile(
        r'^(?P<export>export\s+)?type\s+(?P<name>[A-Za-z0-9_$]+)\s*=',
        re.MULTILINE,
    )
    ENUM_REGEX = re.compile(
        r'^(?P<export>export\s+)?enum\s+(?P<name>[A-Za-z0-9_$]+)',
        re.MULTILINE,
    )
    IMPORT_REGEX = re.compile(
        r'^import\s+(?:(?P<default>[A-Za-z0-9_$]+)|(?:\{\s*(?P<named>[^}]+)\s*\}))\s+from\s+[\'"](?P<source>[^\'"]+)[\'"]',
        re.MULTILINE,
    )

    def parse(self, file_path: str, content: str) -> ParseResult:
        symbols: list[SymbolData] = []
        imports: list[ImportData] = []
        exports: list[ExportData] = []
        lines = content.splitlines()

        # Parse Functions
        for m in self.FN_REGEX.finditer(content):
            name = m.group("name")
            is_exported = bool(m.group("export"))
            is_async = bool(m.group("async"))
            params = m.group("params") or ""
            start_line = content[: m.start()].count("\n") + 1
            # Simple bracket block end heuristic
            end_line = min(start_line + 25, len(lines))

            symbols.append(
                SymbolData(
                    name=name,
                    kind="function",
                    start_line=start_line,
                    end_line=end_line,
                    signature=f"function {name}({params})",
                    is_exported=is_exported,
                    is_async=is_async,
                )
            )

        # Parse Arrow Functions
        for m in self.ARROW_FN_REGEX.finditer(content):
            name = m.group("name")
            is_exported = bool(m.group("export"))
            is_async = bool(m.group("async"))
            params = m.group("params") or ""
            start_line = content[: m.start()].count("\n") + 1
            end_line = min(start_line + 20, len(lines))

            symbols.append(
                SymbolData(
                    name=name,
                    kind="function",
                    start_line=start_line,
                    end_line=end_line,
                    signature=f"const {name} = ({params}) =>",
                    is_exported=is_exported,
                    is_async=is_async,
                )
            )

        # Parse Classes
        for m in self.CLASS_REGEX.finditer(content):
            name = m.group("name")
            is_exported = bool(m.group("export"))
            start_line = content[: m.start()].count("\n") + 1
            end_line = min(start_line + 50, len(lines))

            symbols.append(
                SymbolData(
                    name=name,
                    kind="class",
                    start_line=start_line,
                    end_line=end_line,
                    signature=f"class {name}",
                    is_exported=is_exported,
                )
            )

        # Parse Interfaces
        for m in self.INTERFACE_REGEX.finditer(content):
            name = m.group("name")
            is_exported = bool(m.group("export"))
            start_line = content[: m.start()].count("\n") + 1
            end_line = min(start_line + 15, len(lines))

            symbols.append(
                SymbolData(
                    name=name,
                    kind="interface",
                    start_line=start_line,
                    end_line=end_line,
                    signature=f"interface {name}",
                    is_exported=is_exported,
                )
            )

        # Parse Types & Enums
        for m in self.TYPE_REGEX.finditer(content):
            name = m.group("name")
            is_exported = bool(m.group("export"))
            start_line = content[: m.start()].count("\n") + 1
            symbols.append(
                SymbolData(
                    name=name,
                    kind="type",
                    start_line=start_line,
                    end_line=start_line + 2,
                    signature=f"type {name}",
                    is_exported=is_exported,
                )
            )

        for m in self.ENUM_REGEX.finditer(content):
            name = m.group("name")
            is_exported = bool(m.group("export"))
            start_line = content[: m.start()].count("\n") + 1
            symbols.append(
                SymbolData(
                    name=name,
                    kind="enum",
                    start_line=start_line,
                    end_line=start_line + 10,
                    signature=f"enum {name}",
                    is_exported=is_exported,
                )
            )

        # Parse Imports
        for m in self.IMPORT_REGEX.finditer(content):
            source = m.group("source")
            is_external = not source.startswith(".")
            if m.group("default"):
                imports.append(ImportData(source=source, imported_symbol=m.group("default"), is_external=is_external))
            elif m.group("named"):
                for sym in m.group("named").split(","):
                    sym_clean = sym.strip().split(" as ")[0]
                    if sym_clean:
                        imports.append(ImportData(source=source, imported_symbol=sym_clean, is_external=is_external))

        ast_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return ParseResult(symbols=symbols, imports=imports, exports=exports, ast_hash=ast_hash)
