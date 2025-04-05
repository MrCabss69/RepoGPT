# repogpt/parsers/yaml_parser.py
import logging
from pathlib import Path
from typing import Any, Dict

from .base import Parser, register_parser
from ..utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines

logger = logging.getLogger(__name__)

# Dependencia opcional
try:
    import yaml
    pyyaml_available = True
    logger_yaml = logging.getLogger(__name__) # Logger específico si queremos
    logger_yaml.debug("PyYAML encontrado.")
except ImportError:
    yaml = None
    pyyaml_available = False
    logging.warning("PyYAML no instalado. No se parsearán archivos YAML.")
    logging.warning("Instala con: pip install repogpt[yaml]") # Asumiendo extra 'yaml'

class YamlParser(Parser):
    """Parsea archivos YAML (.yaml, .yml)."""

    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta cargar el archivo YAML y extrae claves principales."""
        logger.debug("Parseando archivo YAML: %s", file_path)
        result: Dict[str, Any] = {'top_level_keys': [], 'structure_preview': None}

        if not pyyaml_available:
            result['_error'] = 'PyYAML library not installed'
            return result

        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_info['line_count'] = len(content.splitlines())

            # Cargar el documento YAML
            data = yaml.safe_load(content)

            if isinstance(data, dict):
                result['top_level_keys'] = list(data.keys())
                # Crear una vista previa de la estructura (simplificada)
                result['structure_preview'] = self._get_structure_preview(data)
            elif isinstance(data, list):
                 result['top_level_keys'] = [f"list_item_{i}" for i in range(min(len(data), 5))] # Max 5 items
                 result['structure_preview'] = 'List'
            else:
                 result['structure_preview'] = type(data).__name__ # Scalar?

            result['blank_lines'] = count_blank_lines(content)

            # Extraer comentarios YAML (#) y TODOs/FIXMEs
            yaml_line_patterns = [r'^\s*#\s*(.*)'] # Asegura que # esté al inicio (después de espacios)
            comments = extract_comments_from_content(content, line_comment_patterns=yaml_line_patterns)
            result['comments_count'] = len(comments)
            result['todos_fixmes'] = extract_todos_fixmes_from_comments(comments)


        except yaml.YAMLError as e:
             logger.warning("Error de sintaxis YAML en %s: %s", file_path, e)
             result['_error'] = f'YAML syntax error: {e}'
        except Exception as e:
            logger.error("Error inesperado parseando YAML %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected YAML parsing error: {e}'

        return result

    def _get_structure_preview(self, data: Any, depth=0, max_depth=2) -> Any:
        """Genera una vista previa de la estructura YAML/Dict."""
        if depth > max_depth:
            return '...'

        if isinstance(data, dict):
            preview = {}
            for k, v in data.items():
                preview[k] = self._get_structure_preview(v, depth + 1, max_depth)
            return preview
        elif isinstance(data, list):
             # Mostrar tipo de los primeros N elementos
             if not data: 
                 return []
             preview_items = [self._get_structure_preview(item, depth + 1, max_depth) for item in data[:3]] # Max 3 items
             return preview_items + (['...'] if len(data) > 3 else [])
        else:
            # Para valores escalares, solo mostrar el tipo
            return type(data).__name__

# Registrar si PyYAML está disponible
if pyyaml_available:
    register_parser('.yaml', YamlParser)
    register_parser('.yml', YamlParser)