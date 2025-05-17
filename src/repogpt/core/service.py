from __future__ import annotations

import sys

import structlog

from repogpt.core.ports import CollectorPort, PipelinePort, PublisherPort
from repogpt.models import AnalysisConf

# === Service ===


class CodeRepoAnalysisService:
    def __init__(
        self, collector: CollectorPort, pipeline: PipelinePort, publisher: PublisherPort
    ):
        self.collector = collector
        self.pipeline = pipeline
        self.publisher = publisher
        self.log = structlog.get_logger(__name__)

    def run(self, runtime_conf: AnalysisConf) -> None:
        col = self.collector.collect(runtime_conf)
        results = [self.pipeline.process(p, runtime_conf) for p in col.files]

        failed = [r for r in results if r.root is None]
        ok = len(results) - len(failed)
        self.log.info("pipeline finished", ok=ok, failed=len(failed))

        if failed and runtime_conf.fail_fast:
            self.log.error("aborting — fail-fast", first_error=failed[0].error)
            sys.exit(1)

        self.publisher.publish(results, runtime_conf)
        if runtime_conf.fail_fast:
            if failed or ok == 0:  # aborta si hay fallos o nada procesado
                self.log.error("aborting — fail-fast", first_error=failed[0].error)
                sys.exit(1)
