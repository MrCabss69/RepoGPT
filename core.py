# ORIGINAL SOURCE SCRIPT: https://github.com/zackees/gptrepo
# ORIGINAL IDEA: https://github.com/mpoon/gpt-repository-loader
# REFACTOR BY: [@MrCabss69]
# Mon Mar 11 2024

import argparse 
import os
from tree_builder import TreeBuilder

    
def main():
    """
    Ejecuta el script de análisis del repositorio: analiza los argumentos de la línea de comandos, procesa el repositorio y escribe la salida.
    """
    parser = argparse.ArgumentParser(description="Enhanced repository processing script.")
    parser.add_argument("repo_path", nargs="?", default=os.getcwd(), help="Path to the git repository")
    parser.add_argument("--extensions", nargs="+", default=['.py'], help="File extensions to process (always includes .md)")
    parser.add_argument("--start_path", default="", help="Subdirectory path to start the analysis")
    args = parser.parse_args()

    tree = TreeBuilder(args.repo_path, args.extensions, args.start_path)
    repo_info = tree.build_tree()
    output_file = "example.txt"
    tree.write_output(repo_info, output_file)
    print(f"Repository contents written to {output_file}")


if __name__ == "__main__":
    main()