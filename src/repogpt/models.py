from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class AnalysisConf:
    repo_path: Path
    include_tests: bool = False
    max_file_size: int = 2_000_000
    languages: list[str] | None = None
    output: Path | None = None
    flatten_kind: str = "node"
    output_format: str = "json"
    to_stdout: bool = False
    # --- phase‑3 ---
    log_level: str = "INFO"  # DEBUG | INFO
    fail_fast: bool = False  # abort on first parser error


@dataclass
class ParserInput:
    file_path: Path
    file_info: dict[str, Any]


@dataclass
class CodeNode:
    id: str
    type: str
    name: str | None = None
    language: str | None = None
    path: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    docstring: str | None = None
    comments: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    parent_id: str | None = None
    children: list[CodeNode] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.type}:{self.name} @{self.start_line}-{self.end_line}>"


@dataclass
class PipelineResult:
    path: Path
    language: str
    root: CodeNode | None
    error: str | None = None
    file_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectionResult:
    files: list[Path]
    skipped: list[Path]
    types: list[str] | None = None


class ParserInterface(Protocol):
    def parse(self, input: ParserInput) -> CodeNode: ...


class ProcessorInterface(Protocol):
    def process(self, root: CodeNode) -> CodeNode: ...
