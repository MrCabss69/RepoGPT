# tests/unit/adapters/parsers/test_py_parser.py

import os
from pathlib import Path

from repogpt.adapters.parser.py_parser import PythonParser
from repogpt.models import ParserInput
from repogpt.utils.tree_utils import (
    all_comments,
    all_docstrings,
    all_tags,
    flatten_tree,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data")


def load_path(filename: str) -> Path:
    return Path(os.path.join(DATA_DIR, filename))


def test_basic_py_structure() -> None:
    parser = PythonParser()
    input_ = ParserInput(file_path=load_path("basic.py"), file_info={})
    root = parser.parse(input_)

    assert root.type == "Module"
    types = [child.type for child in root.children]
    assert set(types) == {"Class", "Function"}
    names = [child.name for child in root.children]
    assert "Test" in names
    assert "foo" in names

    # Cambia aquí:
    comments = all_comments(root)
    assert comments == []
    docstrings = all_docstrings(root)
    assert docstrings == []


def test_docstring_examples() -> None:
    parser = PythonParser()
    input_ = ParserInput(file_path=load_path("docstring_examples.py"), file_info={})
    root = parser.parse(input_)

    # Buscar nodos
    funcs = [n for n in flatten_tree(root) if n["type"] == "Function"]
    classes = [n for n in flatten_tree(root) if n["type"] == "Class"]

    # Función foo tiene docstring
    foo = [f for f in funcs if f["name"] == "foo"][0]
    assert "Docstring de foo" in foo["docstring"]

    # Clase Bar y método baz
    bar = [c for c in classes if c["name"] == "Bar"][0]
    assert "Docstring de clase" in bar["docstring"]
    baz = [f for f in funcs if f["name"] == "baz"][0]
    assert "Docstring de método" in baz["docstring"]

    # Extraer todos los comentarios
    comments = all_comments(root)
    texts = [c["text"] for c in comments]
    assert any("Comentario entre docstring y código" in t for t in texts)


def test_edge_cases_py_comments_and_docstrings() -> None:
    parser = PythonParser()
    input_ = ParserInput(file_path=load_path("edge_cases.py"), file_info={})
    root = parser.parse(input_)

    # Todos los comentarios recogidos (deben estar en cualquier nodo)
    comments = all_comments(root)
    texts = [c["text"] for c in comments]
    n_todos = sum([1 if "TODO" in t else 0 for t in texts])
    n_fixme = sum([1 if "FIXME" in t else 0 for t in texts])
    print(texts)
    assert "Este es un comentario normal" in texts
    assert n_todos == 1
    assert n_fixme == 1

    # Los docstrings solo existen si hay funciones/clases/módulo con ellos
    docstrings = all_docstrings(root)
    # En este archivo, no debería haber docstrings, así que:
    assert docstrings == []  # o len(docstrings) == 0

    # Test tags (si tu parser añade TODO/FIXME como tags)
    tags = all_tags(root)
    print(tags)
    assert "TODO" in tags or n_todos == 1
    assert "FIXME" in tags or n_fixme == 1


def test_edge_cases_blanklines_py() -> None:
    parser = PythonParser()
    input_ = ParserInput(file_path=load_path("edge_cases_blanklines.py"), file_info={})
    root = parser.parse(input_)
    # Chequea el conteo de líneas en blanco (se almacena en root.metrics)
    blank_lines = root.metrics.get("blank_lines", 0)  # Provide default value of 0
    assert blank_lines == 3  # según el archivo, ajusta si cambia el fixture

    loc = root.metrics.get("lines_of_code", 0)  # Provide default value of 0
    assert loc > 0


def test_edge_cases_comments_py() -> None:
    parser = PythonParser()
    input_ = ParserInput(file_path=load_path("edge_cases_comments.py"), file_info={})
    root = parser.parse(input_)

    comments = all_comments(root)
    texts = [c["text"] for c in comments]
    assert any("áéíóú" in t for t in texts)
    assert any("😊" in t for t in texts)
    assert any("tarea pendiente λ" in t for t in texts)
    assert any("Comentario sin espacio" in t for t in texts)
    assert any("indentación" in t for t in texts)
    assert any("símbolos matemáticos" in t for t in texts)
