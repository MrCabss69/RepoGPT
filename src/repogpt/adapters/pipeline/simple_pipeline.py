"""Pipeline: parser + (opcional) processor; captura errores."""

from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar


import structlog

from repogpt.core.ports import PipelinePort
from repogpt.models import (
    AnalysisConf,
    CodeNode,
    ParserInput,
    PipelineResult,
)
from repogpt.utils.file_utils import calculate_file_hash

logger = structlog.get_logger(__name__)

T_co = TypeVar("T_co", bound=CodeNode)


class Parser(Protocol):
    def parse(self, input: ParserInput) -> CodeNode: ...


class Processor(Protocol, Generic[T_co]):
    def __call__(self, node: T_co) -> T_co: ...


class SimplePipeline(PipelinePort):
    def __init__(
        self,
        parsers: dict[str, Parser],
        processors: dict[str, Processor[Any]] | None = None,
    ) -> None:
        self.parsers = parsers
        self.processors = processors or {}

    # ------------------------------------------------------------------
    def process(self, file: Path, conf: AnalysisConf) -> PipelineResult:  # noqa: D401
        ext = file.suffix.lower().lstrip(".")
        file_info = {
            "size": file.stat().st_size,
            "sha256": calculate_file_hash(file),
        }

        parser = self.parsers.get(ext)
        if parser is None:
            return PipelineResult(
                path=file,
                language=ext,
                root=None,
                error="no parser",
                file_info=file_info,
            )

        try:
            root = parser.parse(ParserInput(file, file_info))
            for processor in self.processors.values():
                root = processor(root)
            return PipelineResult(
                path=file, language=ext, root=root, file_info=file_info
            )
        except Exception as exc:  # noqa: BLE001 – queremos capturarlo todo
            tb_short = "\n".join(
                traceback.format_exception_only(type(exc), exc)
            ).strip()
            logger.exception("pipeline error", path=file, error=tb_short)
            return PipelineResult(
                path=file, language=ext, root=None, error=tb_short, file_info=file_info
            )
