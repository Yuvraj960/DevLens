from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SymbolData:
    name: str
    kind: str  # function, method, class, interface, type, enum, variable, constant
    start_line: int
    end_line: int
    signature: str | None = None
    docstring: str | None = None
    is_exported: bool = False
    is_async: bool = False


@dataclass
class ImportData:
    source: str
    imported_symbol: str | None = None
    is_external: bool = False


@dataclass
class ExportData:
    exported_symbol: str


@dataclass
class ParseResult:
    symbols: list[SymbolData] = field(default_factory=list)
    imports: list[ImportData] = field(default_factory=list)
    exports: list[ExportData] = field(default_factory=list)
    ast_hash: str = ""


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, content: str) -> ParseResult:
        """Parse source code content and extract symbols, imports, and exports."""
        pass
