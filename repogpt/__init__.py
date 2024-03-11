import argparse
import os
from repogpt.tree_build import TreeBuilder

def main():
    """
    Execute the repository analysis script: Parses command line arguments, processes the repository, and writes the output.
    """
    parser = argparse.ArgumentParser(description="Enhanced repository processing script.")
    parser.add_argument("repo_path", nargs="?", default=os.getcwd(), help="Path to the git repository")
    parser.add_argument("--extensions", nargs="+", default=['.py'], help="File extensions to process")
    parser.add_argument("--start_path", default="", help="Subdirectory path to start the analysis")
    parser.add_argument("--output", default="example.txt", help="Output file name")
    args = parser.parse_args()

    # Ensure .md files are always included
    if '.md' not in args.extensions:
        args.extensions.append('.md')

    try:
        tree = TreeBuilder(args.repo_path, args.extensions, args.start_path)
        repo_info = tree.build_tree()
        TreeBuilder.write_output(repo_info, args.output)
        print(f"Repository contents written to {args.output}")
    except Exception as e:
        print(f"Error processing the repository: {e}")

if __name__ == "__main__":
    main()
