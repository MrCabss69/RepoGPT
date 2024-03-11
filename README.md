# RepoGPT

RepoGPT is an advanced tool designed to analyze code repositories, generating detailed and structured project summaries. Inspired by the gpt-repository-loader and gptrepo tools, RepoGPT makes it easier to understand the structure and components of a project, optimizing its integration with platforms such as ChatGPT.

## Main Features

- **File Analysis:** RepoGPT performs a deep scan of the files in the repository, collecting crucial information such as line count, classes and their methods, independent functions and associated docstrings.

- **Improved Documentation:** The tool places special emphasis on the clarity and quality of code documentation, promoting good practices such as the use of clear nomenclatures for variables and detailed docstrings.


## Detailed Summon Options

RepoGPT allows you to customize the analysis using the following options:

- `--repo_path`: Specifies the path to the repository to analyze. By default, the current directory is used.
  
- `--extensions`: Defines the file extensions to include in the analysis. By default, .md files are included.
  
- `--start_path`: Allows you to start the analysis from a specific subdirectory of the repository.

**Example:**

```bash
python3 run.py --repo_path /path/to/repo --extensions .py .js --start_path src
```

## Using RepoGPT

To start using RepoGPT, follow these simple steps:

1. **Clone the Repository:**

     ```bash
     git clone https://github.com/MrCabss69/RepoGPT.git
     ```


2. **Navigate to Directory:** Open a terminal or command line and navigate to the directory where the script is located.
     ```bash
     cd repoGPT
     ```
  
3. **Run the Script:** Run the script using Python, providing the necessary arguments as described in the flexible input features.
     ```bash
     python3 run.py
     ```

## Example

```python
import argparse
from tree_builder import TreeBuilder

def main():
      # Script description and command line argument analysis
      tree = TreeBuilder(args.repo_path, args.extensions, args.start_path)
      repo_info = tree.build_tree()
      output_file = "example.txt"
      tree.write_output(repo_info, output_file)
      print(f"Repository contents written to {output_file}")

if __name__ == "__main__":
      main()
```

The TreeBuilder class handles most of the analysis, including extracting information from files, analyzing classes and functions, and generating the project summary.


## Output Structure

RepoGPT organizes the analysis results into a clear and concise structure, including:

- **Project Summary:** Presents an overview of the project through the content of key files such as README.md and IDEA.md.

- **Implementation Summary:** Details specific technical aspects in DEVELOPING.md and offers a structured view of the project, similar to the tree command, enriched with details such as the number of lines per file.

- **Detailed Analysis per File:** Breaks down the functionality of each file, highlighting relevant classes, methods and docstrings.
