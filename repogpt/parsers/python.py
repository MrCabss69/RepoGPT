# ==================== INICIO: ./parsers/python.py ====================
# repogpt/parsers/python.py

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Union
import tokenize


from .base import Parser, register_parser
from ..utils.text_processing import extract_todos_fixmes_from_comments, count_blank_lines

logger = logging.getLogger(__name__)

def get_comment_text(comment_token: tokenize.TokenInfo) -> str:
    """Extrae el texto limpio de un token de comentario."""
    text = comment_token.string.lstrip('#').strip()
    # Opcional: Podrías quitar prefijos comunes como '#:', '# ' si quieres
    return text

class PythonParser(Parser):
    """
    Parsea archivos Python (.py) usando ast y tokenize.
    Extrae una estructura ordenada de elementos: imports, comentarios,
    clases (con métodos y docstrings) y funciones (con docstrings).
    """

    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el archivo Python para extraer su estructura ordenada."""
        logger.debug("Parseando archivo Python: %s", file_path)
        result: Dict[str, Any] = {'structure': [], 'todos_fixmes': {'todos': [], 'fixmes': []}}
        content: str = ""
        try:
            # Leer contenido primero para tokenize y ast
            with file_path.open('rb') as fp:
                # Tokenize para obtener comentarios y su posición
                tokens = list(tokenize.tokenize(fp.readline))
            # Necesitamos el contenido como string para AST
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_info['line_count'] = len(content.splitlines())

            # Extraer comentarios y contar líneas en blanco usando tokens
            comments = []
            # blank_lines = 0
            # raw_lines = content.splitlines() # Necesario para contar líneas en blanco que tokenize ignora a veces
            # all_todos: List[Dict[str, Any]] = []
            # all_fixmes: List[Dict[str, Any]] = []
            # comment_pattern = re.compile(r'(TODO|FIXME)[\s:]?(.*)', re.IGNORECASE)

            for token in tokens:
                if token.type == tokenize.COMMENT:
                    comments.append({
                        'type': 'comment', # Mantener tipo por ahora si se usa
                        'line': token.start[0],
                        'text': get_comment_text(token) # Usar la función existente
                    })
                # Contar NL y líneas vacías asociadas (puede ser menos preciso que splitlines)
                # if token.type == tokenize.NL: # NL token indica fin de línea lógica
                #    if token.line and not token.line.strip(): # Si la línea asociada está vacía
                #         blank_lines += 1
                # elif token.type == tokenize.NEWLINE: # NEWLINE indica fin de stmt, puede haber líneas vacías
                #     # Este enfoque es más complejo con tokenize, usemos splitlines
                #     pass

            # Usar splitlines para contar líneas en blanco de forma fiable
            result['blank_lines'] = count_blank_lines(content)

            # Extraer TODOs/FIXMEs de los comentarios extraídos
            result['todos_fixmes'] = extract_todos_fixmes_from_comments(comments)
            result['comments_count'] = len(comments) # Conteo total de comentarios '#'

            # Parsear con AST
            tree = ast.parse(content, filename=str(file_path))

            # Combinar elementos AST y comentarios
            structure_elements = []
            for node in tree.body: # Iterar solo sobre los nodos de nivel superior
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    structure_elements.append(self._parse_import(node))
                elif isinstance(node, ast.ClassDef):
                    structure_elements.append(self._parse_class(node))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    structure_elements.append(self._parse_function(node))
                # Ignorar otros tipos de nodos de nivel superior por ahora (Assign, Expr, etc.)
                # Podríamos añadir nodos 'code_block' para código suelto si fuera necesario.

            # Fusionar comentarios y elementos AST, luego ordenar por línea de inicio
            combined_elements = comments + structure_elements
            # Asegurar que todos tengan line_start antes de ordenar
            valid_elements = [elem for elem in combined_elements if 'line_start' in elem]
            result['structure'] = sorted(valid_elements, key=lambda x: x['line_start'])

            # Limpiar campos antiguos para evitar confusión (opcional pero recomendado)
            result.pop('classes', None)
            result.pop('functions', None)
            result.pop('imports', None)


        except FileNotFoundError:
            logger.error("Archivo no encontrado durante parsing: %s", file_path)
            return {'_error': 'File not found during parse'}
        except tokenize.TokenError as e:
            logger.warning("Error de tokenización en %s: %s", file_path, e)
            result['_error'] = f'Tokenization error: {e}'
            # Intentar parsear AST igualmente si es posible? O fallar aquí? Fallar es más seguro.
            return result
        except UnicodeDecodeError:
             logger.error("Error de decodificación en %s", file_path)
             return {'_error': 'Unicode decode error'}
        except SyntaxError as e:
            logger.warning("Error de sintaxis AST en %s: %s", file_path, e)
            result['_error'] = f'Syntax error: line {e.lineno}, offset {e.offset}: {e.msg}'
            result['structure'] = []
            # Mantener comentarios si se extrajeron antes del error
            existing_comments = [elem for elem in result.get('structure', []) if elem.get('type') == 'comment']
            result['structure'] = sorted(existing_comments, key=lambda x: x['line_start'])

        except Exception as e:
            logger.error("Error inesperado parseando Python %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected Python parsing error: {e}'
            result['structure'] = []

        return result

    def _get_node_end_lineno(self, node: ast.AST) -> int:
        """Obtiene la línea final de un nodo AST, manejando nodos sin end_lineno."""
        return getattr(node, 'end_lineno', node.lineno)

    def _parse_import(self, node: Union[ast.Import, ast.ImportFrom]) -> Dict[str, Any]:
        """Extrae información de una declaración de import."""
        if isinstance(node, ast.Import):
            value = f"import {', '.join(alias.name + (f' as {alias.asname}' if alias.asname else '') for alias in node.names)}"
        else: 
            module_name = node.module or '.' * node.level
            imports = ', '.join(alias.name + (f' as {alias.asname}' if alias.asname else '') for alias in node.names)
            value = f"from {module_name} import {imports}"
        return {
            'type': 'import',
            'line_start': node.lineno,
            'line_end': self._get_node_end_lineno(node),
            'value': value
        }

    def _parse_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extrae información detallada de una definición de clase y su cuerpo."""
        class_info = {
            'type': 'class',
            'name': node.name,
            'docstring': ast.get_docstring(node, clean=False) or None, # Mantener indentación original
            'line_start': node.lineno,
            'line_end': self._get_node_end_lineno(node),
            'bases': self._get_qual_names(node.bases),
            'decorators': self._get_decorator_names(node.decorator_list),
            'body': []
        }
        # Parsear cuerpo de la clase (métodos, asignaciones, comentarios internos, etc.)
        # Nota: Los comentarios dentro de la clase ya fueron extraídos por tokenize - Aquí solo procesamos nodos AST dentro de la clase.
        body_elements = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                 # Pasar clean=False para mantener la indentación original del docstring
                body_elements.append(self._parse_function(item, is_method=True, clean_docstring=False))
            # Podríamos añadir parsing para asignaciones de atributos de clase aquí si es necesario
            # elif isinstance(item, ast.Assign):
            #     body_elements.append({'type': 'assignment', ...})
            # elif isinstance(item, ast.Pass): continue # Ignorar pass
            # else: # Otros nodos (Expr, etc.)
            #     try: body_elements.append({'type': 'code', 'line_start': item.lineno, 'line_end': self._get_node_end_lineno(item), 'value': ast.unparse(item)})
            #     except: pass # Ignorar si no se puede unparse

        class_info['body'] = sorted(body_elements, key=lambda x: x['line_start'])
        return class_info

    def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], is_method=False, clean_docstring=True) -> Dict[str, Any]:
        """Extrae información detallada de una definición de función/método."""
        func_type = 'method' if is_method else 'function'
        return {
            'type': func_type,
            'name': node.name,
            'docstring': ast.get_docstring(node, clean=clean_docstring) or None,
            'line_start': node.lineno,
            'line_end': self._get_node_end_lineno(node),
            'arguments': self._format_arguments(node.args),
            'returns': ast.unparse(node.returns) if hasattr(node, 'returns') and node.returns and hasattr(ast, 'unparse') else None,
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'decorators': self._get_decorator_names(node.decorator_list)
        }

    def _get_decorator_names(self, decorator_list: List[ast.expr]) -> List[str]:
         """Intenta obtener los nombres de los decoradores usando ast.unparse."""
         names = []
         for d in decorator_list:
             try:
                 # ast.unparse (Python 3.9+) da la representación más fiel
                 names.append(f"@{ast.unparse(d)}")
             except AttributeError:
                 if isinstance(d, ast.Name):
                    names.append(f"@{d.id}")
                 elif isinstance(d, ast.Call) and isinstance(d.func, ast.Name):
                    names.append(f"@{d.func.id}(...)")
                 else: 
                    names.append(f"@decorator(...)")
         return names

    def _get_qual_names(self, nodes: List[ast.expr]) -> List[str]:
         """Intenta obtener nombres calificados (ej. module.Class) usando ast.unparse."""
         names = []
         for node in nodes:
             try:
                  names.append(ast.unparse(node)) # Requiere Python 3.9+
             except AttributeError:
                tmp = node.id if isinstance(node, ast.Name) else "complex_base"
                names.append(tmp)
         return names

    def _format_arguments(self, args: ast.arguments) -> List[str]:
        """Formatea los argumentos de una función/método a una lista de strings."""
        formatted_args = []
        # all_args = args.posonlyargs + args.args + args.kwonlyargs # Combinar posonlyargs, args, kwonlyargs

        # Obtener valores por defecto (requiere mapeo inverso)
        defaults = args.defaults
        kw_defaults = args.kw_defaults
        num_args_with_defaults = len(defaults)
        num_pos_kw_args = len(args.args)

        # Mapear args normales con sus defaults (desde el final)
        arg_defaults = {}
        if num_args_with_defaults > 0:
            for i in range(num_args_with_defaults):
                arg_index = num_pos_kw_args - num_args_with_defaults + i
                if arg_index >= 0 and arg_index < len(args.args):
                     arg_defaults[args.args[arg_index].arg] = defaults[i]

        # Mapear kwonly args con sus defaults
        kwonly_defaults = {}
        for i, arg in enumerate(args.kwonlyargs):
             if kw_defaults[i] is not None:
                 kwonly_defaults[arg.arg] = kw_defaults[i]

        arg_index_counter = 0
        # Positional-only arguments
        for arg in args.posonlyargs:
            arg_str = arg.arg
            if arg.annotation: 
                arg_str += f": {ast.unparse(arg.annotation)}" if hasattr(ast,'unparse') else ": Type"
            # Defaults para posonly son parte de 'defaults' antes que los de 'args'
            if arg_index_counter < len(defaults) - num_args_with_defaults :
                try: 
                    arg_str += f" = {ast.unparse(defaults[arg_index_counter])}" if hasattr(ast,'unparse') else " = ..."
                except: 
                    arg_str += " = ..."
            formatted_args.append(arg_str)
            arg_index_counter += 1

        if args.posonlyargs: 
            formatted_args.append('/')
        # Regular arguments
        for arg in args.args:
            arg_str = arg.arg
            if arg.annotation: 
                arg_str += f": {ast.unparse(arg.annotation)}" if hasattr(ast,'unparse') else ": Type"
            if arg.arg in arg_defaults:
                try: 
                    arg_str += f" = {ast.unparse(arg_defaults[arg.arg])}" if hasattr(ast,'unparse') else " = ..."
                except: 
                    arg_str += " = ..."
            formatted_args.append(arg_str)

        # Vararg (*args)
        if args.vararg:
            arg_str = f"*{args.vararg.arg}"
            if args.vararg.annotation:
                arg_str += f": {ast.unparse(args.vararg.annotation)}" if hasattr(ast,'unparse') else ": Type"
            formatted_args.append(arg_str)

        # Keyword-only arguments
        if args.kwonlyargs and not args.vararg:
             formatted_args.append('*') # Separador si no hay *args
        for arg in args.kwonlyargs:
            arg_str = arg.arg
            if arg.annotation: 
                arg_str += f": {ast.unparse(arg.annotation)}" if hasattr(ast,'unparse') else ": Type"
            if arg.arg in kwonly_defaults:
                try: 
                    arg_str += f" = {ast.unparse(kwonly_defaults[arg.arg])}" if hasattr(ast,'unparse') else " = ..."
                except:
                    arg_str += " = ..."
            formatted_args.append(arg_str)

        # Kwarg (**kwargs)
        if args.kwarg:
            arg_str = f"**{args.kwarg.arg}"
            if args.kwarg.annotation:
                arg_str += f": {ast.unparse(args.kwarg.annotation)}" if hasattr(ast,'unparse') else ": Type"
            formatted_args.append(arg_str)

        return formatted_args


# Registrar el parser
register_parser('.py', PythonParser)
# ==================== FIN: ./parsers/python.py ======================