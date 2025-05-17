import json
import subprocess
from pathlib import Path
from typing import Any

REPO_FIXTURE = Path(__file__).parent / "data"


def _run(extra_args: list[str]) -> str:
    cmd = [
        "repogpt",
        *extra_args,
        "--include-tests",  # asegurar que Directorios 'tests' no se excluyan
        str(REPO_FIXTURE),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return proc.stdout


def _json_lines(stdout: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in stdout.strip().split("\n") if line.strip()]


def test_languages_filter() -> None:
    out = _run(
        ["--languages", "py", "--stdout", "--format", "ndjson", "--flatten", "file"]
    )
    objs = _json_lines(out)
    assert objs, "expected at least one object"
    assert all(o["lang"] == "py" for o in objs)


def test_ndjson_file_lines() -> None:
    out = _run(["--stdout", "--format", "ndjson", "--flatten", "file"])
    objs = _json_lines(out)
    py_files = set(REPO_FIXTURE.glob("*.py"))
    md_files = set(REPO_FIXTURE.glob("*.md"))
    expected = [p for p in (py_files | md_files) if p.name != "bad.py"]
    assert len(objs) == len(expected)
