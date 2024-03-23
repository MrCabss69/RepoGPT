import argparse
from pathlib import Path
from repogpt.tree_build import TreeBuilder

def main():
    parser = argparse.ArgumentParser(description="Enhanced repository processing script.")
    parser.add_argument("repo_path", nargs="?", default=Path.cwd(), help="Path to the git repository")
    parser.add_argument("--output", default="example.txt", help="Output file name")
    args = parser.parse_args()

    try:
        repo_path = Path(args.repo_path).resolve()
        tree = TreeBuilder(repo_path)
        repo_info = tree.build_tree()
        output_path = Path(args.output)
        tree.write_output(repo_info, output_path)
        print(f"Repository contents written to {output_path}")
    except Exception as e:
        print(f"Error processing the repository: {e}")


if __name__ == "__main__":
    main()
