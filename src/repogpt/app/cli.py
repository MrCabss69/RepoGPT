from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import structlog

from repogpt.adapters.collector.simple_collector import SimpleCollector
from repogpt.adapters.parser import parsers
from repogpt.adapters.pipeline.simple_pipeline import SimplePipeline
from repogpt.adapters.publisher.simple_publisher import SimplePublisher
from repogpt.core.service import CodeRepoAnalysisService
from repogpt.models import AnalysisConf

LEVELS: dict[str, int] = {"DEBUG": logging.DEBUG, "INFO": logging.INFO}


def _configure_logging(level: str) -> None:
    logging.basicConfig(level=LEVELS[level], format="%(message)s", stream=sys.stderr)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(LEVELS[level]),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )


def main() -> int:  # noqa: D401
    parser = argparse.ArgumentParser(
        description="Analyze a code repository and output structured summaries.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("repo_path")
    parser.add_argument("--include-tests", action="store_true")
    parser.add_argument("--flatten", choices=["node", "file"], default="node")
    parser.add_argument("--format", choices=["json", "ndjson"], default="json")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("-o", "--output")
    parser.add_argument("--languages")
    # phase‑3 flags
    parser.add_argument("--log-level", choices=["INFO", "DEBUG"], default="INFO")
    parser.add_argument("--fail-fast", action="store_true")

    args = parser.parse_args()

    _configure_logging(args.log_level)
    log = structlog.get_logger()

    langs = (
        [s.strip().lower() for s in args.languages.split(",")]
        if args.languages
        else None
    )
    to_stdout = args.stdout or (
        args.output and Path(args.output).as_posix() == "/dev/stdout"
    )

    conf = AnalysisConf(
        repo_path=Path(args.repo_path).resolve(),
        include_tests=args.include_tests,
        output=None if to_stdout else Path(args.output) if args.output else None,
        flatten_kind=args.flatten,
        output_format=args.format,
        to_stdout=to_stdout,
        languages=langs,
        log_level=args.log_level,
        fail_fast=args.fail_fast,
    )

    log.info("starting run", repo=str(conf.repo_path), format=conf.output_format)

    CodeRepoAnalysisService(
        collector=SimpleCollector(),
        pipeline=SimplePipeline(parsers=parsers, processors={}),
        publisher=SimplePublisher(),
    ).run(runtime_conf=conf)

    return 0


if __name__ == "__main__":
    sys.exit(main())
