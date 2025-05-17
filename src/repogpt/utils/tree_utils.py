import dataclasses
from collections.abc import Callable
from typing import Any

from repogpt.models import CodeNode


def flatten_tree(root: CodeNode) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    def walk(node: CodeNode) -> None:
        d = dataclasses.asdict(node).copy()
        d.pop("children")
        result.append(d)
        for child in node.children:
            walk(child)

    walk(root)
    return result


# === Query-tree utils


def nodes_by_type(root: CodeNode, type_: str) -> list[dict[str, Any]]:
    """Devuelve todos los nodos del árbol de un tipo dado."""
    return [n for n in flatten_tree(root) if n["type"] == type_]


def all_comments(root: CodeNode) -> list[dict[str, Any]]:
    """Devuelve todos los comentarios de todos los nodos."""
    return [c for n in flatten_tree(root) for c in n.get("comments", [])]


def all_docstrings(root: CodeNode) -> list[str | None]:
    """Devuelve todos los docstrings de los nodos (si existen)."""
    return [n["docstring"] for n in flatten_tree(root) if n.get("docstring")]


def all_tags(root: CodeNode) -> list[str]:
    """Devuelve todos los tags de todos los nodos."""
    return [tag for n in flatten_tree(root) for tag in n.get("tags", [])]


# Avanzado: filtrado por predicado arbitrario
def nodes_where(
    root: CodeNode, predicate: Callable[[dict[str, Any]], bool]
) -> list[dict[str, Any]]:
    """Devuelve nodos que cumplen una condición arbitraria."""
    return [n for n in flatten_tree(root) if predicate(n)]
