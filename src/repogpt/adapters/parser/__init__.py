"""Registro global de parsers soportados."""

from repogpt.adapters.parser.md_parser import MarkdownParser
from repogpt.adapters.parser.py_parser import PythonParser

parsers = {
    "py": PythonParser(),
    "md": MarkdownParser(),
}
