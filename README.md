# RepoGPT

> **Abstraction, summarization and code intelligence — built for both humans and LLMs**

RepoGPT turns a source-tree into a *consultable abstraction layer*:  
structured, queryable and ready for downstream indexing or RAG pipelines.

```

\[Collector] → \[Parser] → \[Processor] → \[Publisher]
\|            |              |             |
paths      CodeNode-trees  optional     JSON / NDJSON / stdout

```

* **Languages** – Python (`.py`) & Markdown (`.md`) out-of-the-box.  
  Extendable via plug-in parsers.  
* **Outputs** – hierarchical or flat, single-file JSON or streaming NDJSON.  
* **Logging** – powered by `structlog`; fully STDOUT-safe.  
* **Fail-fast** – abort immediately on the first parser error if you need strict runs.
* **Ignore rules** – `.repogptignore` (git-wildmatch) + sensible defaults (`.git`, `node_modules`, …).

---

## Installation

```bash
git clone https://github.com/MrCabss69/RepoGPT.git
cd RepoGPT
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"           # installs structlog, pathspec, pytest, ruff…
```

---

## Desarrollo y Calidad de Código

Este proyecto utiliza [pre-commit](https://pre-commit.com) para asegurar calidad automática:

- **Linting y autoformato** (`black`, `ruff`)
- **Chequeo de tipado** (`mypy`)
- **Tests unitarios y cobertura ≥80%** (`pytest --cov`)

**¿Cómo contribuyo de forma segura?**

1. Instala pre-commit (una vez):
    ```
    pip install pre-commit
    pre-commit install
    ```

2. Antes de commitear, ejecuta todos los checks:
    ```
    pre-commit run --all-files
    ```

> Si algún check falla, **arregla el código antes de push/PR**.  
> El pipeline de CI es igual de estricto.


---

## Quick start

```bash
# analyse a codebase and emit a single JSON file
repogpt path-to-project/ -o report.json

# NDJSON one-line-per-file, streamed to stdout (great for pipes)
repogpt path-to-project/  --flatten node --format ndjson --stdout | jq 'select(.type=="Class")'

```

---

## CLI reference

| Flag                       | Default         | Description                                                                                                                     |
| -------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `--flatten {node,file}`    | `node`          | *node*: every `CodeNode` appears (can explode to many lines).<br>*file*: only the root node (tree) per file.                    |
| `--format {json,ndjson}`   | `json`          | Output container.<br>*json*: single list written to file.<br>*ndjson*: one JSON object per line (either node or file as above). |
| `--stdout`                 | -               | Stream to STDOUT instead of file.<br>Passing `-o /dev/stdout` has the same effect.                                              |
| `-o, --output PATH`        | `analysis.json` | Destination file (ignored if `--stdout`).                                                                                       |
| `--languages "py,md,ts"`   | all parsers     | Comma-separated, case-insensitive whitelist of extensions.                                                                      |
| `--include-tests`          | *off*           | Do **not** skip `tests/` or `test_*.py`.                                                                                        |
| `--log-level {INFO,DEBUG}` | `INFO`          | Structured logs to STDERR.                                                                                                      |
| `--fail-fast`              | *off*           | Abort on the first parser error (exit 1).                                                                                       |

### Exit codes

| Code | Meaning                                         |
| ---- | ----------------------------------------------- |
| `0`  | All requested files parsed successfully.        |
| `1`  | Fail-fast triggered or unrecoverable CLI error. |

---

## `.repogptignore`

Use the same glob syntax as `.gitignore` to exclude paths or files **in addition** to built-ins such as `.git/`, `node_modules/`, `__pycache__/`, etc.

```gitignore
# ignore generated docs
docs/build/

# ignore big assets
*.png
*.pdf
```

---

## Output examples

### 1. JSON (flatten=node)

```json
[
  {
    "id": "…",
    "type": "Module",
    "name": "utils",
    "path": "src/repogpt/utils/text_processing.py",
    "lang": "py",
    "metrics": { "lines_of_code": 180, "blank_lines": 40 },
    …
  },
  { "id": "…", "type": "Function", "name": "extract_comments", … },
  …
]
```

### 2. NDJSON (flatten=file)

```text
{"id":"…","type":"Module", ... ,"path":"README.md","lang":"md"}
{"id":"…","type":"Module", ... ,"path":"src/repogpt/__init__.py","lang":"py"}
```

---

## Logging & diagnostics

RepoGPT never mixes **data** and **logs**:

* Data → STDOUT (`--stdout`) or the output file.
* Logs → STDERR (via `structlog`).

Examples:

```text
2025-05-17 18:12:07 [info ] starting run          format=ndjson repo=/path/to/repo
2025-05-17 18:12:07 [debug] skip                  path=tests/foo.py reason=ignored
2025-05-17 18:12:08 [error] aborting — fail-fast  first_error="SyntaxError: invalid syntax"
```

Capture with `pytest`’s `caplog`, or redirect STDERR to a file in CI.

---

## Development

```bash
ruff check .
mypy src/
pytest -q
```

### Project layout

```
src/repogpt/
├── adapters/
│   ├── collector/      # filesystem traversal & ignore logic
│   ├── parser/         # language-specific parsers → CodeNode trees
│   ├── pipeline/       # glue + processors
│   └── publisher/      # JSON/NDJSON writer
├── core/               # service + clean-architecture ports
├── utils/              # file & text helpers
└── app/cli.py          # entry-point
```

### Extending to another language

1. Create `src/repogpt/adapters/parser/<lang>_parser.py` implementing `parse() → CodeNode`.
2. Register it in `adapters/parser/__init__.py`.
3. Add extension to docs and tests.

---

## Tests

```
pytest                                 # full unit/integration suite
pytest tests/test_phase3.py -q         # logging & fail-fast happy-path
```

The suite exercises:

* Collect / ignore rules
* Markdown & Python parsers (fixtures under `tests/data/`)
* NDJSON vs JSON writer
* Fail-fast & debug logging

---

## Roadmap

* **Phase 4** – caching by file-hash + parallel workers
* **Phase 5** – CI (ruff + mypy + pytest), release to PyPI
* **Phase 6** – plug-in entry-points for custom processors & new languages
* **Phase 7** – optional HTML / graph visualizer

---

## License

[MIT](LICENSE)

Happy hacking 💻