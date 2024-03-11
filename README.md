# RepoGPT

RepoGPT is a tool based on: [gpt-repository-loader](https://github.com/mpoon/gpt-repository-loader) and [gptrepo](https://github.com/zackees/gptrepo), designed to generate fast and detailed summaries of projects or repositories. These summaries are optimized to be consumed directly by ChatGPT, making it easy to understand the project without the need for additional context.

## Characteristics

- **File Analysis:** RepoGPT extracts detailed information from each file in the repository, including line counts, docstrings, classes with their independent methods and functions.
  
  
- **Improved Documentation:** Includes detailed docstrings for functions and clear variable nomenclature, which improves the readability and maintainability of the code.
  

## Output Structure

The result of the analysis with RepoGPT is structured as follows:

- **Project Summary:** Includes the contents of key files such as README.md and IDEA.md, providing an immediate overview of the project.
  
- **Implementation Summary:** Technical details about the implementation are summarized in DEVELOPING.md, along with a project structure similar to the tree command, enhanced with the number of lines per file.
  
- **Summary of Each File:** The functionality of each file is included, extracting information from headers and docstrings, if available. Additionally, classes are named and functions are listed per class.

## Use

To use RepoGPT, follow these steps:

1. **Clone Repository:** Clone the repository containing the RepoGPT script to your local machine.
  
2. **Navigate to Directory:** Open a terminal or command line and navigate to the directory where the script is located.
  
3. **Run the Script:** Run the script using Python, providing the necessary arguments as described in the flexible input features.

Code example:

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



# TODOs:
Make a module for easy Python usage 