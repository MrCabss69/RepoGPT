from pathlib import Path
import pytest

from repogpt.adapters.collector.simple_collector import SimpleCollector
from repogpt.models import AnalysisConf


def test_collect_ignores_git_files(tmp_path: Path) -> None:
    # Preparo un repo con .git, .gitignore y archivos .py / .pyc
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("test")
    (tmp_path / ".gitignore").write_text("*.pyc\n__pycache__/\n")
    (tmp_path / "main.py").write_text("print('test')")
    (tmp_path / "test.pyc").write_text("test")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "test.pyc").write_text("test")

    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=tmp_path)
    result = collector.collect(conf)

    assert len(result.files) == 1
    assert result.files[0].name == "main.py"


def test_collect_respects_repogptignore(tmp_path: Path) -> None:
    # Ahora usamos .repogptignore en lugar de argumentos al constructor
    (tmp_path / ".repogptignore").write_text("*.py\n__pycache__/\n")
    (tmp_path / "keep.py").write_text("print('ok')")
    (tmp_path / "skip.py").write_text("print('no')")
    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=tmp_path)
    result = collector.collect(conf)

    assert len(result.files) == 0


def test_collect_includes_tests_when_requested(tmp_path: Path) -> None:
    (tmp_path / "foo.py").write_text("x=1")
    (tmp_path / "test_foo.py").write_text("x=2")

    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=tmp_path, include_tests=True)
    result = collector.collect(conf)

    names = {f.name for f in result.files}
    assert names == {"foo.py", "test_foo.py"}


def test_collect_excludes_tests_by_default(tmp_path: Path) -> None:
    (tmp_path / "foo.py").write_text("x=1")
    (tmp_path / "test_foo.py").write_text("x=2")

    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=tmp_path, include_tests=False)
    result = collector.collect(conf)

    names = {f.name for f in result.files}
    assert names == {"foo.py"}


def test_collect_empty_directory_returns_empty(tmp_path: Path) -> None:
    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=tmp_path)
    result = collector.collect(conf)
    assert result.files == []


def test_collect_nonexistent_directory_raises(tmp_path: Path) -> None:
    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=Path("no-such-dir"))
    with pytest.raises(FileNotFoundError):
        collector.collect(conf)


def test_collect_file_instead_of_directory_raises(tmp_path: Path) -> None:
    file = tmp_path / "solo.py"
    file.write_text("x=1")
    collector = SimpleCollector()
    conf = AnalysisConf(repo_path=file)
    with pytest.raises(NotADirectoryError):
        collector.collect(conf)
