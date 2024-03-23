# --- TreeBuilder ---
# Analiza el repositorio especificado, extrayendo información detallada de los archivos .py y .md según las extensiones válidas proporcionadas
# Creado por: [@MrCabss69]
# Fecha de creación: Sat Mar 23 2024

import ast
import re
import os
import json

class TreeBuilder:
    
    def __init__(self, repo_path, valid_extensions=None, start_path=''):
        """
        Inicializa el TreeBuilder con la ruta del repositorio, extensiones válidas y un path de inicio opcional.
        
        :param repo_path: Ruta absoluta al repositorio.
        :param valid_extensions: Lista de extensiones de archivo para incluir en el análisis.
        :param start_path: Ruta dentro del repositorio desde donde comenzar el análisis.
        """
        self.repo_path = os.path.abspath(repo_path)
        self.start_path = os.path.abspath(os.path.join(self.repo_path, start_path))
        self.valid_extensions = valid_extensions if valid_extensions else ['.py', '.md']
        self.exclusion_pattern = re.compile(r'^\.|egg-info$|/_|/env$|/venv$|/node_modules')

    def is_excluded(self, path):
        """
        Determina si una ruta dada debe ser excluida del análisis basándose en los patrones de exclusión.

        :param path: Ruta del archivo o directorio a verificar.
        :return: True si la ruta debe ser excluida, False en caso contrario.
        """
        relative_path = os.path.relpath(path, self.start_path)
        return self.exclusion_pattern.search(relative_path) is not None

    def build_tree(self):
        """
        Construye la estructura del árbol del repositorio comenzando desde la ruta de inicio.

        :return: Diccionario representando la estructura del repositorio.
        """
        return self.process_directory(self.start_path)

    def process_directory(self, directory):
        """
        Procesa de manera recursiva cada directorio y archivo en el directorio dado, extrayendo la información relevante.

        :param directory: Ruta del directorio a procesar.
        :return: Diccionario con la información del directorio y sus contenidos.
        """
        repo_info = {}
        for entry in os.scandir(directory):
            if self.is_excluded(entry.path):
                continue

            rel_path = os.path.relpath(entry.path, self.start_path)
            if entry.is_dir():
                repo_info[rel_path] = self.process_directory(entry.path)
            elif entry.is_file() and any(entry.name.endswith(ext) for ext in self.valid_extensions):
                repo_info[rel_path] = self.extract_file_info(entry.path)
        return repo_info

    def extract_file_info(self, file_path):
        """
        Extrae información de un archivo individual, incluyendo el recuento de líneas y, para archivos .py, clases y funciones.

        :param file_path: Ruta al archivo del cual extraer información.
        :return: Diccionario con la información extraída del archivo.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            return {'error': str(e)}

        if file_path.endswith('.md'):
            return {'__type__': 'file', 'content': content.strip()}

        return self.parse_python_content(content)

    def parse_python_content(self, content):
        """
        Analiza el contenido de un archivo Python para extraer clases, funciones y sus docstrings.

        :param content: Contenido del archivo Python.
        :return: Diccionario con las clases y funciones extraídas del contenido.
        """
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {'error': f'Error processing the file: {e}'}

        classes, functions = [], []
        methods = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self.handle_class_node(node)
                classes.append(class_info)
                methods.update(method['name'] for method in class_info['methods'])

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name not in methods:
                functions.append(self.handle_function_node(node))

        return {'classes': classes, 'functions': functions}

    def handle_class_node(self, node):
        """
        Extrae información de un nodo de clase del AST, incluyendo métodos y docstrings.

        :param node: Nodo AST de la clase.
        :return: Diccionario con el nombre de la clase, su docstring y sus métodos.
        """
        methods = [self.handle_function_node(n) for n in node.body if isinstance(n, ast.FunctionDef)]
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'methods': methods
        }

    def handle_function_node(self, node):
        """
        Extrae información de un nodo de función del AST, incluyendo su nombre y docstring.

        :param node: Nodo AST de la función.
        :return: Diccionario con el nombre de la función y su docstring.
        """
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node)
        }

    def write_output(self, repo_info, output_file):
        """
        Escribe la información del repositorio en un archivo de salida. El formato de salida
        se determina por la extensión del archivo: .json para JSON, y cualquier otra cosa para texto plano.

        :param repo_info: Diccionario con la información del repositorio.
        :param output_file: Ruta del archivo de salida donde se escribirá la información.
        """
        if output_file.suffix == '.json':
            with output_file.open('w', encoding='utf-8') as file:
                json.dump(repo_info, file, indent=4)
        else:
            with output_file.open('w', encoding='utf-8') as file:
                self._write_dict(repo_info, file)

    def _write_dict(self, data, file, indent=0):
        """
        Escribe de manera recursiva la información del repositorio en formato de texto plano.

        :param data: Datos a escribir.
        :param file: Descriptor de archivo abierto.
        :param indent: Nivel actual de indentación.
        """
        for key, value in data.items():
            prefix = " " * indent
            if isinstance(value, dict):
                if indent == 0:
                    file.write(f"{prefix}## {key}\n")
                else:
                    file.write(f"{prefix}- {key}/:\n")
                self._write_dict(value, file, indent + 4)
            else:
                if key == '__type__' and value == 'file':
                    continue
                if isinstance(value, list):
                    for item in value:
                        if 'name' in item and 'docstring' in item:
                            file.write(f"{prefix}### {item['name']}\n")
                            if item['docstring']:
                                file.write(f"{prefix}  Docstring: {item['docstring']}\n")
                            if 'methods' in item:  # Si tiene métodos, listamos cada uno
                                for method in item['methods']:
                                    file.write(f"{prefix}    - {method['name']}: {method['docstring']}\n")
                else:
                    file.write(f"{prefix}- {key}: {value}\n")
