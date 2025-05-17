from pathlib import Path
import uuid

from repogpt.adapters.pipeline.simple_pipeline import SimplePipeline, Processor
from repogpt.models import AnalysisConf, CodeNode, ParserInput


class MockParser:
    def parse(self, input: ParserInput) -> CodeNode:
        # Devuelve siempre un nodo raíz muy básico
        return CodeNode(
            id=str(uuid.uuid4()),
            type="module",
            name="test",
            language="py",
            path=str(input.file_path),
            start_line=1,
            end_line=1,
            children=[],
        )


class MockProcessor(Processor[CodeNode]):
    def __call__(self, node: CodeNode) -> CodeNode:
        node.name = "processed"
        return node


def test_process_success(tmp_path: Path) -> None:
    # Creo un archivo de prueba
    fp = tmp_path / "test.py"
    contenido = "print('hola')"
    fp.write_text(contenido, encoding="utf-8")

    parser = MockParser()
    processor: Processor[CodeNode] = MockProcessor()
    pipeline = SimplePipeline(parsers={"py": parser}, processors={"py": processor})
    conf = AnalysisConf(repo_path=tmp_path)

    result = pipeline.process(fp, conf)

    assert result.path == fp
    assert result.language == "py"
    assert result.file_info["size"] == len(contenido)
    assert isinstance(result.file_info.get("sha256"), str)
    assert result.root is not None
    assert result.root.name == "processed"
    assert result.error is None


def test_process_no_parser(tmp_path: Path) -> None:
    fp = tmp_path / "test.py"
    fp.write_text("x=1", encoding="utf-8")

    pipeline = SimplePipeline(parsers={}, processors={})
    conf = AnalysisConf(repo_path=tmp_path)
    result = pipeline.process(fp, conf)

    assert result.path == fp
    assert result.language == "py"
    assert result.root is None
    assert result.error == "no parser"


def test_process_parser_error(tmp_path: Path) -> None:
    class ErrorParser:
        def parse(self, input: ParserInput) -> CodeNode:
            raise ValueError("test error")

    fp = tmp_path / "boom.py"
    fp.write_text("x=1", encoding="utf-8")

    pipeline = SimplePipeline(parsers={"py": ErrorParser()}, processors={})
    conf = AnalysisConf(repo_path=tmp_path)
    result = pipeline.process(fp, conf)

    assert result.path == fp
    assert result.language == "py"
    assert result.root is None
    assert result.error is not None
    assert "test error" in result.error


def test_process_no_processors(tmp_path: Path) -> None:
    fp = tmp_path / "plain.py"
    fp.write_text("x=2", encoding="utf-8")

    parser = MockParser()
    pipeline = SimplePipeline(parsers={"py": parser}, processors={})
    conf = AnalysisConf(repo_path=tmp_path)
    result = pipeline.process(fp, conf)

    assert result.root is not None
    assert result.root.name == "test"
    assert result.error is None
