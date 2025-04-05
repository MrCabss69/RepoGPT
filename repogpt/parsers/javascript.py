# repogpt/parsers/javascript.py
import logging
import re
from pathlib import Path
from typing import Any, Dict, Set

from .base import Parser, register_parser
from ..utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines

logger = logging.getLogger(__name__)

try:
    from pyjsparser import PyJsParser, JsSyntaxError # Intentar importar pyjsparser
    pyjsparser_available = True
    logger.debug("pyjsparser encontrado. Se usará para análisis AST de JS/TS.")
except ImportError:
    PyJsParser = None
    JsSyntaxError = None
    pyjsparser_available = False
    logger.warning("pyjsparser no instalado. El análisis de JS/TS se basará en Regex (menos preciso).")
    logger.warning("Instala con: pip install repogpt[js]")

class JavaScriptParser(Parser):
    """Parsea archivos JavaScript/TypeScript (.js, .jsx, .ts, .tsx)."""

    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta usar AST si está disponible, si no, usa Regex."""
        logger.debug("Parseando archivo JS/TS: %s", file_path)
        result: Dict[str, Any] = {
            'imports': [], 'exports': [], 'functions': [],
            'classes': [], 'components': [], 'todos_fixmes': {}
        }
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_info['line_count'] = len(content.splitlines())

            if pyjsparser_available:
                try:
                    parser = PyJsParser()
                    # Nota: pyjsparser puede tener problemas con sintaxis moderna (TS, JSX)
                    # Podría ser necesario un parser más robusto (ej. esprima-python, o llamar a node/babel externo)
                    parsed_ast = parser.parse(content)
                    # --- Implementar extracción desde el AST de pyjsparser ---
                    # Esto es un placeholder, se necesitaría recorrer el AST ('body', etc.)
                    # para encontrar declaraciones de funciones, clases, exports, imports...
                    # Ejemplo muy básico (no funcional):
                    # for node in parsed_ast.get('body', []):
                    #    if node.get('type') == 'FunctionDeclaration':
                    #        result['functions'].append(node.get('id', {}).get('name'))
                    #    elif node.get('type') == 'ExportNamedDeclaration':
                    #        # ... extraer exports
                    #    elif node.get('type') == 'ImportDeclaration':
                    #        # ... extraer imports
                    result['ast_parsed'] = True # Indicar que se usó AST
                    # logger.warning("Extracción AST desde pyjsparser aún no implementada detalladamente.")
                except (JsSyntaxError, RecursionError, Exception) as ast_err:
                    # Manejar errores de parsing AST o si pyjsparser falla con sintaxis compleja
                    logger.warning("Fallo al parsear %s con pyjsparser AST (%s). Usando Regex como fallback.", file_path, ast_err)
                    result.update(self._parse_with_regex(content))
                    result['ast_parse_error'] = str(ast_err)
            else:
                # Usar Regex si pyjsparser no está disponible
                result.update(self._parse_with_regex(content))

                result['blank_lines'] = count_blank_lines(content)

                # Definir patrones de comentario JS
                js_line_patterns = [r'//\s*(.*)']
                js_block_patterns = [('/*', '*/')] # Tupla de strings literales

                # Extraer comentarios y TODOs/FIXMEs
                comments = extract_comments_from_content(content,
                                                        line_comment_patterns=js_line_patterns,
                                                        block_comment_patterns=js_block_patterns)
                result['comments_count'] = len(comments)
                result['todos_fixmes'] = extract_todos_fixmes_from_comments(comments)

                # Continuar con el parsing AST o Regex...
                if pyjsparser_available:
                    # ... (lógica AST)
                    pass # Asegúrate de que el código AST no dependa de los métodos eliminados
                else:
                    result.update(self._parse_with_regex(content))
                    # Asegúrate de que _parse_with_regex no dependa de los métodos eliminados
     
        except Exception as e:
            logger.error("Error inesperado parseando JS/TS %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected JS/TS parsing error: {e}'

        return result

    def _parse_with_regex(self, content: str) -> Dict[str, Any]:
        """Análisis basado en Regex para JS/TS (menos preciso)."""
        regex_result: Dict[str, Any] = {'imports': [], 'exports': [], 'functions': [], 'classes': [], 'components': []}
        imports: Set[str] = set()
        exports: Set[str] = set()
        functions: Set[str] = set()
        classes: Set[str] = set()
        components: Set[str] = set()

        # Imports (simplificado)
        # import ... from '...' / import '...' / require('...')
        import_pattern = re.compile(r'import(?:[\s\S]*?)from\s+[\'"]([^\'"]+)[\'"]|import\s+[\'"]([^\'"]+)[\'"]|require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)', re.MULTILINE)
        for match in import_pattern.finditer(content):
            imports.add(match.group(1) or match.group(2) or match.group(3))

        # Exports (simplificado)
        # export function ..., export class ..., export const ..., export default ...
        export_pattern = re.compile(r'export\s+(?:default\s+)?(?:function|class|const|let|var)\s+([a-zA-Z_$][\w$]*)', re.MULTILINE)
        exports.update(export_pattern.findall(content))

        # Functions (simplificado - function name(...) or const name = (...) => {...})
        func_pattern = re.compile(r'(?:function\s+([a-zA-Z_$][\w$]*)\s*\(|const\s+([a-zA-Z_$][\w$]*)\s*=\s*(?:async\s*)?\([\s\S]*?\)\s*=>)', re.MULTILINE)
        for match in func_pattern.finditer(content):
            functions.add(match.group(1) or match.group(2))

        # Classes (simplificado)
        class_pattern = re.compile(r'class\s+([a-zA-Z_$][\w$]*)(?:\s+extends\s+[\w$.]+)?', re.MULTILINE)
        classes.update(class_pattern.findall(content))

        # React Components (simplificado - empieza con Mayúscula)
        # Podría coincidir con clases normales, necesita refinamiento
        component_pattern = re.compile(r'(?:function|class)\s+([A-Z]\w*)\s*(?:\(|\{|extends)', re.MULTILINE)
        components.update(component_pattern.findall(content))

        regex_result['imports'] = sorted(list(imports))
        regex_result['exports'] = sorted(list(exports))
        regex_result['functions'] = sorted(list(functions))
        regex_result['classes'] = sorted(list(classes))
        regex_result['components'] = sorted(list(components))
        regex_result['parsed_with'] = 'regex'
        return regex_result



# Registrar para extensiones JS/TS/JSX/TSX
register_parser('.js', JavaScriptParser)
register_parser('.jsx', JavaScriptParser)
register_parser('.ts', JavaScriptParser)
register_parser('.tsx', JavaScriptParser)