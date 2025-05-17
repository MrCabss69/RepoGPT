"""Ports: firmas ajustadas pero conceptualmente iguales."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from repogpt.models import AnalysisConf, CollectionResult, PipelineResult


class CollectorPort(Protocol):
    def collect(self, conf: AnalysisConf) -> CollectionResult:  # noqa: D401
        ...


class PipelinePort(Protocol):
    def process(self, file: Path, conf: AnalysisConf) -> PipelineResult:  # noqa: D401
        ...


class PublisherPort(Protocol):
    def publish(
        self, results: list[PipelineResult], conf: AnalysisConf
    ) -> None:  # noqa: D401
        ...
