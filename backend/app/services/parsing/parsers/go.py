import hashlib
import re
from app.services.parsing.base import BaseParser, ExportData, ImportData, ParseResult, SymbolData


class GoParser(BaseParser):
    """Lexical & AST parser for Go source files."""

    FUNC_REGEX = re.compile(
        r'^func\s+(?:\((?P<receiver>[^)]+)\)\s+)?(?P<name>[A-Za-z0-9_]+)\s*\((?P<params>[^)]*)\)',
        re.MULTILINE,
    )
    STRUCT_REGEX = re.compile(
        r'^type\s+(?P<name>[A-Za-z0-9_]+)\s+struct\b',
        re.MULTILINE,
    )
    INTERFACE_REGEX = re.compile(
        r'^type\s+(?P<name>[A-Za-z0-9_]+)\s+interface\b',
        re.MULTILINE,
    )
    IMPORT_REGEX = re.compile(
        r'import\s+(?:\(\s*(?P<block>[^)]+)\s*\)|"(?P<single>[^"]+)")',
        re.DOTALL,
    )

    def parse(self, file_path: str, content: str) -> ParseResult:
        symbols: list[SymbolData] = []
        imports: list[ImportData] = []
        exports: list[ExportData] = []
        lines = content.splitlines()

        # Parse Functions & Receiver Methods
        for m in self.FUNC_REGEX.finditer(content):
            name = m.group("name")
            receiver = m.group("receiver")
            params = m.group("params") or ""
            start_line = content[: m.start()].count("\n") + 1
            end_line = min(start_line + 30, len(lines))
            is_exported = name[0].isupper() if name else False
            kind = "method" if receiver else "function"

            sig = f"func ({receiver}) {name}({params})" if receiver else f"func {name}({params})"

            symbols.append(
                SymbolData(
                    name=name,
                    kind=kind,
                    start_line=start_line,
                    end_line=end_line,
                    signature=sig,
                    is_exported=is_exported,
                )
            )

        # Parse Structs
        for m in self.STRUCT_REGEX.finditer(content):
            name = m.group("name")
            start_line = content[: m.start()].count("\n") + 1
            end_line = min(start_line + 20, len(lines))
            is_exported = name[0].isupper() if name else False

            symbols.append(
                SymbolData(
                    name=name,
                    kind="struct",
                    start_line=start_line,
                    end_line=end_line,
                    signature=f"type {name} struct",
                    is_exported=is_exported,
                )
            )

        # Parse Interfaces
        for m in self.INTERFACE_REGEX.finditer(content):
            name = m.group("name")
            start_line = content[: m.start()].count("\n") + 1
            end_line = min(start_line + 15, len(lines))
            is_exported = name[0].isupper() if name else False

            symbols.append(
                SymbolData(
                    name=name,
                    kind="interface",
                    start_line=start_line,
                    end_line=end_line,
                    signature=f"type {name} interface",
                    is_exported=is_exported,
                )
            )

        # Parse Imports
        for m in self.IMPORT_REGEX.finditer(content):
            if m.group("single"):
                imports.append(ImportData(source=m.group("single"), is_external=True))
            elif m.group("block"):
                for line in m.group("block").splitlines():
                    clean_line = line.strip().strip('"')
                    if clean_line and not clean_line.startswith("//"):
                        imports.append(ImportData(source=clean_line, is_external=True))

        ast_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return ParseResult(symbols=symbols, imports=imports, exports=exports, ast_hash=ast_hash)
