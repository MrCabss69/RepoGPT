# repogpt/parsers/generic.py
import logging
from pathlib import Path
from typing import Any, Dict, List

from .base import Parser # No se registra, es un fallback
# Importar utils actualizadas
from ..utils.text_processing import (
    extract_comments_from_content,
    extract_todos_fixmes_from_comments
)


logger = logging.getLogger(__name__)

class GenericTextParser(Parser):
    """Parser genérico para archivos de texto no reconocidos por otros parsers."""

    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae información básica como conteo de líneas y TODOs/FIXMEs usando streaming."""
        logger.debug("Parseando archivo genérico (streaming): %s", file_path)
        result: Dict[str, Any] = {'content_preview': '', 'todos_fixmes': {}, 'comments_count': 0, 'blank_lines': 0}
        lines_buffer: List[str] = []
        line_count = 0
        preview_char_count = 0
        PREVIEW_LIMIT = 500

        try:
            with file_path.open('r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    # --- Procesamiento línea por línea ---
                    line_count += 1
                    if not line.strip():
                        result['blank_lines'] += 1

                    # Almacenar para preview (solo lo necesario)
                    if preview_char_count < PREVIEW_LIMIT:
                         lines_buffer.append(line)
                         preview_char_count += len(line)

                    # Podríamos aplicar regex de comentarios/todos aquí línea por línea
                    # pero extract_comments_from_content necesita el contenido completo.
                    # Mantenemos el enfoque actual por simplicidad, pero sacrificando
                    # el beneficio completo del streaming para estas extracciones.
                    # Si la memoria fuera crítica, habría que refactorizar las utils
                    # para que acepten iteradores o procesen línea a línea.

            file_info['line_count'] = line_count

            # Reconstruir contenido solo si es necesario (para preview y análisis completo)
            # Si el archivo es muy grande, esto anula parcialmente el beneficio del stream
            # Podríamos limitar la reconstrucción o el análisis posterior.
            content = "".join(lines_buffer) # Contenido parcial para preview
            if preview_char_count >= PREVIEW_LIMIT:
                 # Si leímos más allá del límite, truncar y añadir puntos
                 # Necesitaríamos leer el archivo completo para hacer bien el análisis de comentarios/todos
                 # Aquí hacemos un compromiso: analizamos solo el preview
                 logger.warning("Analizando solo el preview (%d bytes) para comentarios/todos en archivo grande %s",
                                PREVIEW_LIMIT, file_path)
                 result['content_preview'] = content[:PREVIEW_LIMIT] + '...'
                 # Leer el archivo completo para un análisis preciso (¡anula el streaming!)
                 # content_full = file_path.read_text(encoding='utf-8', errors='replace')
                 # O aceptar el análisis sobre el preview:
                 content_for_analysis = content[:PREVIEW_LIMIT]

            else:
                 result['content_preview'] = content
                 content_for_analysis = content # El preview es el contenido completo

            # Intentar extraer TODOs/FIXMEs genéricos (buscar en comentarios #, //)
            # Usar content_for_analysis (que puede ser solo el preview)
            generic_line_patterns = [r'^\s*#\s*(.*)', r'^\s*//\s*(.*)']
            comments = extract_comments_from_content(content_for_analysis, line_comment_patterns=generic_line_patterns)
            result['comments_count'] = len(comments)
            result['todos_fixmes'] = extract_todos_fixmes_from_comments(comments)


        except FileNotFoundError:
             logger.error("Archivo no encontrado durante parsing genérico: %s", file_path)
             return {'_error': f'File not found: {file_path}'}
        except Exception as e:
            logger.error("Error inesperado parseando archivo genérico %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected generic parsing error: {e}'
            # Poner line_count si se alcanzó a calcular
            if line_count > 0: file_info['line_count'] = line_count


        return result