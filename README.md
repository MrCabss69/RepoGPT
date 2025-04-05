# RepoGPT

RepoGPT analyzes software repos and creates structured summaries suitable for fast ingestion by Large Language Models (LLMs) or for human review. It iterates through project directories, parses various file types, extracts structural information, metadata, tasks , and generates comprehensive reports in Markdown or JSON formats.

Inspired by [gpt-repository-loader](https://github.com/mpoon/gpt-repository-loader) and [gptrepo](https://github.com/zackees/gptrepo/tree/main).

# Features

*   **Detailed Code Structure:** Extracts classes, methods, functions, interfaces (from TS), imports, decorators, and docstrings, presenting them hierarchically.
*   **Broad Language Support:** Parses Python, JavaScript, TypeScript (JSX/TSX), Markdown, YAML, HTML, Dockerfiles, and provides basic analysis for other text files.
*   **Metadata Extraction:** Gathers information from Git (branch, commit, author), project dependencies (package.json, requirements.txt, pyproject.toml, etc.), and calculates code metrics (line counts, size, file types).
*   **Task Identification:** Aggregates `TODO` and `FIXME` comments found within the codebase.
*   **Configurable Markdown Output:** Generates rich Markdown reports (default) with syntax highlighting hints. Use flags (`--summary`, `--dependencies`, `--tasks`, `--file-metadata`) to control the level of detail included in the report.
*   **JSON Output:** Provides a complete dump of all extracted data in JSON format (`-f json`).
*   **Concurrency:** Processes files in parallel for faster analysis.
*   **.gitignore Integration:** Respects `.gitignore` rules to exclude irrelevant files (can be disabled with `--no-gitignore`).
*   **Customizable Analysis:** Allows specifying start subdirectories, maximum file size, and selecting specific data extractors.


# Installing

## Prerequisites

*   Python 3.9+
*   Git (Required for extracting Git information via the `git` extractor)

## Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/MrCabss69/RepoGPT.git
    ```

2.  **Navigate to the Project Directory:**
    ```bash
    cd RepoGPT
    ```

3.  **Install the module (Editable Mode Recommended):**
    *   Using `pip`:
        ```bash
        pip install -e .
        ```
    *   *Optional Dependencies:* For full language/feature support, install extras:
        *   JavaScript/TypeScript parsing (`pyjsparser`): `pip install -e .[js]`
        *   YAML parsing (`PyYAML`): `pip install -e .[yaml]`
        *   Gitignore parsing (`gitignore-parser`): `pip install -e .[gitignore]`
        *   Install all: `pip install -e .[js,yaml,gitignore]`
    *   *(Note: Define these extras in your `setup.py` or `pyproject.toml`)*

# Using RepoGPT

Navigate to the root directory of the project you want to analyze (or provide the path as an argument) and run the `repogpt` command in your terminal.

**Basic Usage (Default Markdown to Console):**
```bash
repogpt
```

**Analyzing a Different Project Path:**
```bash
repogpt /path/to/other/project
```

**Saving Output to a File:**
```bash
# Save default Markdown report
repogpt -o my_report.md

# Save JSON report
repogpt --format json --output-file my_report.json
# Or shorter: repogpt -f json -o my_report.json
```

**Generating a More Detailed Markdown Report:**
```bash
repogpt --summary --dependencies --tasks --file-metadata -o detailed_report.md
```

**Analyzing a Specific Subdirectory:**
```bash
# Analyze the 'src' folder within the project at 'path/to/your/code'
repogpt path/to/your/code --start-path src -o src_report.md
```


# How To Use - Examples

Here are a few ways to use RepoGPT:

*   **Default Analysis (Markdown to Console):**
    *   Analyzes the current directory (`.`) and prints a standard Markdown report to the console.
    ```bash
    repogpt
    ```

*   **Detailed Markdown Report (Saved to File):**
    *   Includes summary, dependencies, tasks, and file metadata sections in the Markdown report and saves it.
    ```bash
    repogpt --summary --dependencies --tasks --file-metadata -o detailed_report.md
    ```

*   **JSON Output (Saved to File):**
    *   Generates a complete JSON representation of all extracted data.
    ```bash
    repogpt -f json -o report.json
    ```

*   **Analyze a Specific Subdirectory:**
    *   Focuses the analysis only on the `src/` subdirectory within the current project.
    ```bash
    repogpt --start-path src -o src_report.md
    ```

*   **Ignoring `.gitignore` Rules:**
    *   Analyzes all files, even those listed in `.gitignore`.
    ```bash
    repogpt --no-gitignore -o report_including_ignored.md
    ```

*   **Adjusting File Size Limit:**
    *   Processes files up to 10MB instead of the default 2MB limit.
    ```bash
    repogpt --max-file-size 10485760 -o report_large_files.md
    ```

*   **Increasing Parallelism:**
    *   Uses 8 worker threads instead of the default 4 for potentially faster analysis on multi-core machines.
    ```bash
    repogpt --max-workers 8
    ```

*   **Querying JSON Output with `jq`:**
    *   Pipes the JSON output to the `jq` tool to extract specific information (e.g., total file count).
    ```bash
    repogpt -f json | jq '.code_metrics.total_files'
    ```

*(Consider adding links to actual example output files if you generate them)*
*   `example_report.md` (Generated with default options)
*   `example_report_detailed.md` (Generated with detail flags)
*   `example_report.json` (Generated with `-f json`)

# Command-Line Options (Advanced Usage)

*   `repo_path` (Positional): Path to the repository to analyze (default: `.`).
*   `--start-path`: Subdirectory within the repo to start analysis from (relative to `repo_path`, default: "").
*   `-o`, `--output-file`: File path to save the report. If omitted, prints to standard output.
*   `-f`, `--format`: Output format. Choices: `md` (default), `json`.
*   `--extractors`: Comma-separated list of extractors to use (default includes all available: e.g., `dependencies,git,metrics,todos`). *Note: Some extractors might be automatically included if required by report flags like `--summary`.*
*   `--summary`: (Markdown only) Include the Summary section (Git info, Metrics). Requires `git` and `metrics` extractors.
*   `--dependencies`: (Markdown only) Include the detailed Dependencies section. Requires `dependencies` extractor.
*   `--tasks`: (Markdown only) Include the aggregated list of TODOs/FIXMEs. Requires `todos` extractor.
*   `--file-metadata`: (Markdown only) Include detailed metadata (size, hash) per file.
*   `--max-workers`: Max number of threads for file processing (default: 4).
*   `--max-file-size`: Max file size in bytes to process (default: 2MB, e.g., `10485760` for 10MB).
*   `--no-gitignore`: Disable using `.gitignore` rules for filtering.
*   `--log-level`: Set logging detail level (DEBUG, INFO, WARNING, ERROR, CRITICAL; default: INFO). Log messages go to console (stderr) and `repogpt_analyzer.log`.
*   `--version`: Show program's version number and exit.
*   

# Project Structure (RepoGPT Tool Itself)

```bash
    repogpt/
    ├── __init__.py             # Package initializer, version
    ├── __main__.py             # CLI entry point, argument parsing
    ├── analyzer.py             # Core repository analysis logic
    ├── exceptions.py           # Custom exception classes
    │
    ├── extractors/             # Modules for extracting specific data
    │   ├── __init__.py
    │   ├── base.py
    │   ├── dependencies.py
    │   ├── git.py
    │   ├── metrics.py
    │   ├── structure.py        # (Currently not used by default reporter)
    │   └── todos.py
    │
    ├── parsers/                # Modules for parsing different file types
    │   ├── __init__.py
    │   ├── base.py
    │   ├── python.py
    │   ├── javascript.py
    │   ├── markdown.py
    │   ├── yaml_parser.py
    │   ├── html.py
    │   ├── dockerfile_.py      # Parses Dockerfiles
    │   └── generic.py          # Fallback text parser
    │
    ├── reporting/              # Modules for generating reports
    │   ├── __init__.py
    │   ├── base.py
    │   ├── json_reporter.py
    │   └── markdown_reporter.py
    │
    └── utils/                  # Utility functions
        ├── __init__.py
        ├── file_utils.py       # Hashing, binary detection
        ├── gitignore_handler.py # .gitignore parsing logic
        ├── logging.py          # Logging setup
        └── text_processing.py  # Comment/TODO extraction, blank line counting

    README.md
    setup.py                    # Or pyproject.toml for packaging/dependencies
    repogpt_analyzer.log        # Default log file name
```