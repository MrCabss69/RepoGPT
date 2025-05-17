from pathlib import Path

import pathspec
import structlog

from repogpt.adapters.parser import parsers
from repogpt.core.ports import CollectorPort
from repogpt.models import AnalysisConf, CollectionResult
from repogpt.utils.file_utils import is_likely_binary

# Carpeta/archivo siempre ignorados
DEFAULT_IGNORES: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "node_modules",
    ".tox",
    ".DS_Store",
    ".idea",
    ".vscode",
}


def load_pathspec(repo_root: Path) -> pathspec.PathSpec | None:
    ignore_file = repo_root / ".repogptignore"
    if ignore_file.exists():
        with ignore_file.open("r") as f:
            lines = [
                line for line in f if line.strip() and not line.strip().startswith("#")
            ]
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return None


def should_ignore(
    p: Path, repo_root: Path, spec: pathspec.PathSpec | None = None
) -> bool:
    rel = p.relative_to(repo_root)
    # Hardcoded ignores: cualquier parte del path
    if any(part in DEFAULT_IGNORES for part in rel.parts):
        return True
    # Archivos/carpetas ocultas (excepto el root)
    if any(part.startswith(".") and part != "." for part in rel.parts):
        return True
    # Symlinks (no seguimos)
    if p.is_symlink():
        return True
    # pathspec patterns (si .repogptignore existe)
    if spec and spec.match_file(str(rel)):
        return True
    return False


class SimpleCollector(CollectorPort):
    def collect(self, conf: AnalysisConf) -> CollectionResult:

        repo_root = conf.repo_path.resolve()
        # ---------- sanity checks ----------
        if not repo_root.exists():
            raise FileNotFoundError(f"Repository path '{repo_root}' does not exist")
        if not repo_root.is_dir():
            raise NotADirectoryError(
                f"Repository path '{repo_root}' is not a directory"
            )

        allowed_exts = set(conf.languages or parsers.keys())
        spec = load_pathspec(repo_root)
        files: list[Path] = []
        skipped: list[Path] = []
        slogger = structlog.get_logger(__name__)
        for p in repo_root.rglob("*"):
            # Ignorar directorios, symlinks y patrones .repogptignore
            if should_ignore(p, repo_root, spec):
                slogger.debug("skip", path=str(p), reason="ignored")
                skipped.append(p)
                continue
            if not p.is_file():
                continue
            # Solo extensiones soportadas (puedes cambiar según tus parsers)
            allowed_exts = set(
                conf.languages or parsers.keys()
            )  # parsers importado abajo
            if p.suffix.lstrip(".").lower() not in allowed_exts:
                slogger.debug("skip", path=str(p), reason="ignored")
                skipped.append(p)
                continue
            # Excluye tests si así lo pide la conf
            if not conf.include_tests:
                filename = p.parts[-1]
                if "tests" in p.parts or filename.startswith(("test_", "test-")):
                    slogger.debug("skip", path=str(p), reason="ignored")
                    skipped.append(p)
                    continue

            # Filtrar por tamaño y binarios
            if p.stat().st_size > conf.max_file_size or is_likely_binary(p):
                slogger.debug("skip", path=str(p), reason="ignored")
                skipped.append(p)
                continue
            files.append(p)
        return CollectionResult(files=files, skipped=skipped, types=None)
