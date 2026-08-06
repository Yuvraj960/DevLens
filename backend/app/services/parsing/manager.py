from app.services.parsing.base import BaseParser, ParseResult
from app.services.parsing.parsers.go import GoParser
from app.services.parsing.parsers.python import PythonParser
from app.services.parsing.parsers.typescript import TSParser


class LanguageManager:
    """Manages language parser routing based on file extension."""

    def __init__(self):
        self._ts_parser = TSParser()
        self._python_parser = PythonParser()
        self._go_parser = GoParser()

        self._parsers: dict[str, BaseParser] = {
            "typescript": self._ts_parser,
            "javascript": self._ts_parser,
            "python": self._python_parser,
            "go": self._go_parser,
        }

    def get_parser(self, language: str) -> BaseParser | None:
        return self._parsers.get(language.lower())

    def parse_content(self, file_path: str, language: str, content: str) -> ParseResult:
        parser = self.get_parser(language)
        if not parser:
            return ParseResult()
        return parser.parse(file_path, content)


language_manager = LanguageManager()
