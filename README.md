# RepoGPT

RepoGPT is an advanced tool designed to analyze code repositories, generating detailed and structured project summaries. Inspired by the gpt-repository-loader and gptrepo tools, RepoGPT makes it easy to understand the structure and components of a project, optimizing its integration with platforms like ChatGPT.

**Example:**

```tap
python3 run.py --repo_path /path/to/repo --extensions .py .js --start_path src
```


# Using RepoGPT

The project structure and usage process have been updated. Follow these steps to start using RepoGPT:

## Clone the Repository:

```tap
git clone https://github.com/MrCabss69/RepoGPT.git
```

## Navigate to the Project Directory:

Open a terminal or command line and navigate to the root directory of the cloned project.

```tap
cd RepoGPT
```

## Install the module
```tap
pip -e installation.
```

## Run RepoGPT:

Once installed, you can run RepoGPT directly from the command line, providing the necessary arguments as described above.

```tap
repogpt --repo_path /path/to/repo --extensions .py .js --start_path src
```

## Main Features

- **File Analysis:** RepoGPT performs a deep scan of the files in the repository, collecting crucial information such as line count, classes and their methods, independent functions and associated docstrings.

- **Documentation Improvement:** The tool places special emphasis on the clarity and quality of code documentation, promoting good practices such as the use of clear nomenclatures for variables and detailed documentation strings.

## Detailed Analysis Options

RepoGPT allows you to customize the analysis using the following options:

- `--repo_path`: Specifies the path of the repository to analyze. By default, the current directory is used.
- `--extensions`: Defines the file extensions to include in the analysis. By default, .md files are included.
- `--start_path`: Allows you to start the analysis from a specific subdirectory of the repository.

# Structure
```tap.
├── README.md
├── repoppt
│ ├── documents
│ │ ├── DESARROLLO.md
│ │ ├── IDEA.md
│ │ └── TODO.md
│ ├── __init__.py
└── configuration.py

```