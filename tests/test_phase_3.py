import subprocess
from pathlib import Path

REPO = Path(__file__).parent / "data"
BAD_FILE = REPO / "bad.py"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["repogpt", *args, str(REPO)],
        capture_output=True,
        text=True,
    )


def test_fail_fast() -> None:
    proc = _run(["--fail-fast", "--stdout", "--include-tests"])
    assert proc.returncode == 1
    assert "aborting — fail-fast" in proc.stderr


def test_debug_logs() -> None:
    proc = _run(["--stdout", "--log-level", "DEBUG", "--include-tests"])
    assert proc.returncode == 0
    assert "starting run" in proc.stderr


# # cleanup
# BAD_FILE.unlink(missing_ok=True)
