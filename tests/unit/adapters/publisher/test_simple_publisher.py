import json
from pathlib import Path
from typing import Any

from repogpt.adapters.publisher.simple_publisher import SimplePublisher
from repogpt.models import AnalysisConf, CodeNode, PipelineResult


def test_publish_json(tmp_path: Path) -> None:
    output = tmp_path / "out.json"
    conf = AnalysisConf(
        repo_path=tmp_path,
        output=output,
        output_format="json",
        flatten_kind="node",
    )

    node = CodeNode(
        id="1",
        type="module",
        name="test",
        language="py",
        path="test.py",
        start_line=1,
        end_line=1,
        children=[],
    )
    result = PipelineResult(
        path=Path("test.py"),
        language="py",
        root=node,
        file_info={"size": 100},
    )

    publisher = SimplePublisher()
    publisher.publish([result], conf)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["type"] == "module"
    assert data[0]["name"] == "test"
    assert data[0]["path"] == "test.py"
    assert data[0]["lang"] == "py"
    assert data[0]["size"] == 100


def test_publish_ndjson(tmp_path: Path) -> None:
    output = tmp_path / "out.ndjson"
    conf = AnalysisConf(
        repo_path=tmp_path,
        output=output,
        output_format="ndjson",
        flatten_kind="node",
    )

    node = CodeNode(
        id="1",
        type="module",
        name="test",
        language="py",
        path="test.py",
        start_line=1,
        end_line=1,
        children=[],
    )
    result = PipelineResult(
        path=Path("test.py"),
        language="py",
        root=node,
        file_info={"size": 100},
    )

    publisher = SimplePublisher()
    publisher.publish([result], conf)

    lines = output.read_text(encoding="utf-8").splitlines()
    data = [json.loads(line) for line in lines if line.strip()]
    assert len(data) == 1
    assert data[0]["type"] == "module"
    assert data[0]["name"] == "test"
    assert data[0]["path"] == "test.py"
    assert data[0]["lang"] == "py"
    assert data[0]["size"] == 100


def test_publish_stdout(capsys: Any) -> None:
    conf = AnalysisConf(
        repo_path=Path.cwd(),
        to_stdout=True,
        output_format="json",
        flatten_kind="node",
    )
    node = CodeNode(
        id="1",
        type="module",
        name="test",
        language="py",
        path="test.py",
        start_line=1,
        end_line=1,
        children=[],
    )
    result = PipelineResult(
        path=Path("test.py"),
        language="py",
        root=node,
        file_info={"size": 100},
    )

    publisher = SimplePublisher()
    publisher.publish([result], conf)

    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["type"] == "module"
    assert data[0]["name"] == "test"
    assert data[0]["path"] == "test.py"
    assert data[0]["lang"] == "py"
    assert data[0]["size"] == 100


def test_publish_with_error(tmp_path: Path) -> None:
    output = tmp_path / "out.json"
    conf = AnalysisConf(
        repo_path=tmp_path,
        output=output,
        output_format="json",
        flatten_kind="node",
    )
    result = PipelineResult(
        path=Path("test.py"),
        language="py",
        root=None,
        error="err!",
        file_info={"size": 100},
    )

    publisher = SimplePublisher()
    publisher.publish([result], conf)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data == []


def test_publish_empty_results(tmp_path: Path) -> None:
    output = tmp_path / "out.json"
    conf = AnalysisConf(
        repo_path=tmp_path,
        output=output,
        output_format="json",
        flatten_kind="node",
    )
    publisher = SimplePublisher()
    publisher.publish([], conf)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data == []
