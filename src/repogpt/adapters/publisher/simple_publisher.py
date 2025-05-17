"""Publisher que soporta JSON, NDJSON y STDOUT."""

from __future__ import annotations

import dataclasses
import json
import os
import sys
from collections.abc import Generator
from typing import Any

import structlog

from repogpt.core.ports import PublisherPort
from repogpt.models import AnalysisConf, PipelineResult
from repogpt.utils.tree_utils import flatten_tree

logger = structlog.get_logger(__name__)


class SimplePublisher(PublisherPort):
    def _yield_serialized_nodes(
        self, r: PipelineResult, conf: AnalysisConf
    ) -> Generator[dict[str, Any], None, None]:
        """Genera los objetos listos para json.dumps según flatten_kind."""
        if r.root is None:
            return  # fail handled elsewhere

        root = r.root
        if conf.flatten_kind == "node":
            nodes = flatten_tree(root)
        else:  # file
            nodes = [dataclasses.asdict(root)]

        for node in nodes:
            node.update(
                {
                    "path": str(r.path),
                    "lang": r.language,
                    **r.file_info,
                }
            )
            yield node

    # ------------------------------------------------------------------
    def publish(
        self, results: list[PipelineResult], conf: AnalysisConf
    ) -> None:  # noqa: D401
        data_iterables: list[Generator[dict[str, Any], None, None]] = []
        failures = []

        for res in results:
            if res.root is None:
                failures.append({"path": str(res.path), "error": res.error})
                continue
            data_iterables.append(self._yield_serialized_nodes(res, conf))

        def line_iter() -> Generator[dict[str, Any], None, None]:
            for it in data_iterables:
                yield from it

        # Decide sink ---------------------------------------------------
        sink_stdout = (
            conf.to_stdout or conf.output is None and conf.output_format == "ndjson"
        )
        if sink_stdout:
            self._write_stream(line_iter(), conf)
        else:
            output_path = conf.output or os.path.join(os.getcwd(), "analysis.json")
            with open(output_path, "w", encoding="utf-8") as fh:
                if conf.output_format == "json":
                    json.dump(list(line_iter()), fh, ensure_ascii=False, indent=2)
                else:  # ndjson
                    for obj in line_iter():
                        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
            logger.info(
                "analysis saved",
                path=output_path,
                ok=len(results) - len(failures),
                fails=len(failures),
            )

        if failures:
            print("Failed files:", file=sys.stderr)
            for f in failures:
                logger.error("parse error", **f)

    # ------------------------------------------------------------------
    @staticmethod
    def _write_stream(
        objs: Generator[dict[str, Any], None, None], conf: AnalysisConf
    ) -> None:
        """Escribe a stdout según formato."""
        stream = sys.stdout
        if conf.output_format == "json":
            json.dump(list(objs), stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        else:  # ndjson
            for obj in objs:
                stream.write(json.dumps(obj, ensure_ascii=False) + "\n")
