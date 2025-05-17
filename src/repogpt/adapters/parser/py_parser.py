# repogpt/adapters/parser/py_parser.py

import ast
from typing import Any
from uuid import uuid4

from repogpt.models import CodeNode, ParserInput, ParserInterface
from repogpt.utils.text_processing import (
    count_blank_lines,
    extract_comments,
)


class PythonParser(ParserInterface):
    def __init__(self) -> None:
        pass

    def parse(self, input: ParserInput) -> CodeNode:
        path = input.file_path
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content, filename=str(path))

        # --- Root node (Module) ---
        root = CodeNode(
            id=str(uuid4()),
            type="Module",
            name=path.stem,
            language="python",
            path=str(path),
            start_line=1,
            end_line=content.count("\n") + 1,
            metrics={
                "blank_lines": count_blank_lines(content),
                "lines_of_code": len(
                    [line for line in content.splitlines() if line.strip()]
                ),
            },
        )

        # --- Extract comments (flat, will associate later)
        comments = extract_comments(content, language="python")

        # --- Build CodeNode tree ---
        self._visit(tree, parent_node=root)

        # --- Associate comments ---
        self._associate_comments(root, comments)

        return root

    def _visit(self, node: ast.AST, parent_node: CodeNode) -> None:
        """Recursively visit AST nodes and build CodeNode instances."""
        for child in ast.iter_child_nodes(node):
            cn = None
            if isinstance(
                child, ast.Import | ast.ImportFrom
            ):  # <-- nuevo (Python 3.10+)
                cn = self._make_import_node(child, parent_node)
            elif isinstance(child, ast.ClassDef):
                cn = self._make_class_node(child, parent_node)
            elif isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                cn = self._make_function_node(child, parent_node)

            if cn:
                parent_node.children.append(cn)
                self._visit(child, parent_node=cn)
            else:
                # Sigue recorriendo (por si hay anidados, ej: funciones en funciones)
                self._visit(child, parent_node=parent_node)

    def _make_import_node(
        self, node: ast.Import | ast.ImportFrom, parent: CodeNode
    ) -> CodeNode:
        imports = [{"name": a.name, "type": "external"} for a in node.names]
        return CodeNode(
            id=str(uuid4()),
            type="Import",
            name=None,
            path=parent.path,
            parent_id=parent.id,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            dependencies=imports,
            language=parent.language,
        )

    def _make_class_node(self, node: ast.ClassDef, parent: CodeNode) -> CodeNode:
        return CodeNode(
            id=str(uuid4()),
            type="Class",
            name=node.name,
            path=parent.path,
            parent_id=parent.id,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            docstring=ast.get_docstring(node),
            language=parent.language,
        )

    def _make_function_node(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, parent: CodeNode
    ) -> CodeNode:
        return CodeNode(
            id=str(uuid4()),
            type="Function",
            name=node.name,
            path=parent.path,
            parent_id=parent.id,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            docstring=ast.get_docstring(node),
            language=parent.language,
        )

    def _associate_comments(
        self, root: CodeNode, comments: list[dict[str, Any]]
    ) -> None:
        """Attach comments to the smallest containing CodeNode by line range."""

        def walk(node: CodeNode, comment: dict[str, Any]) -> CodeNode | None:
            if (
                node.start_line
                and node.end_line
                and node.start_line <= comment["line"] <= node.end_line
            ):
                for child in node.children:
                    found = walk(child, comment)
                    if found:
                        return found
                return node
            return None

        for comment in comments:
            owner = walk(root, comment) or root
            owner.comments.append(comment)

    def _alias(self, a: ast.alias) -> str:
        return f"{a.name} as {a.asname}" if a.asname else a.name
