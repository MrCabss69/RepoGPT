# repogpt/utils/text_processing.py
import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Patrón general para TODO/FIXME, busca la palabra clave seguida opcionalmente
# por dos puntos o espacio, y captura el resto del mensaje en esa línea/bloque.
TODO_FIXME_PATTERN = re.compile(r'(TODO|FIXME)[\s:]?(.*)', re.IGNORECASE)

def extract_todos_fixmes_from_comments(
    comments: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extrae TODOs y FIXMEs encontrados dentro de una lista de comentarios pre-extraídos.

    Args:
        comments: Una lista de diccionarios, donde cada dict representa un comentario
                  y debe tener al menos las claves 'line' (int o str) y 'text' (str).

    Returns:
        Un diccionario con claves 'todos' y 'fixmes', cada una conteniendo una lista
        de diccionarios {'line': ..., 'message': ...}.
    """
    todos: List[Dict[str, Any]] = []
    fixmes: List[Dict[str, Any]] = []

    for comment in comments:
        comment_text = comment.get('text', '')
        comment_line = comment.get('line', 'unknown') # Mantener 'block' o 'comment' si no hay línea específica

        # Buscar todas las ocurrencias en el texto del comentario
        for match in TODO_FIXME_PATTERN.finditer(comment_text):
            marker = match.group(1).upper()
            message = match.group(2).strip()
            # Eliminar saltos de línea del mensaje si es un comentario multilínea
            message = message.replace('\n', ' ').replace('\r', '')

            entry = {'line': comment_line, 'message': message}
            if marker == 'TODO':
                todos.append(entry)
            else: # FIXME
                fixmes.append(entry)

    return {'todos': todos, 'fixmes': fixmes}

def extract_comments_from_content(
    content: str,
    line_comment_patterns: List[str] = [], # Regex para comentarios de línea (ej. r'^\s*#\s*(.*)')
    block_comment_patterns: List[Tuple[str, str]] = [], # Tuplas de regex (inicio, fin) para bloques (ej. (r'/\*', r'\*/'))
    include_docstrings: bool = False # Placeholder si se quiere añadir extracción genérica de docstrings
) -> List[Dict[str, Any]]:
    """
    Extrae comentarios de un bloque de contenido usando patrones Regex.

    Args:
        content: El contenido completo del archivo como string.
        line_comment_patterns: Lista de patrones regex para comentarios de una línea.
                               El grupo 1 debe capturar el texto del comentario.
        block_comment_patterns: Lista de tuplas (start_regex, end_regex) para comentarios de bloque.
                                La extracción será básica (extrae todo entre start y end).
        include_docstrings: (No implementado aún) Si intentar extraer docstrings genéricos.


    Returns:
        Lista de diccionarios de comentarios {'line': int, 'text': str} o {'line': 'block', 'text': str}.
        El número de línea es aproximado para bloques.
    """
    comments: List[Dict[str, Any]] = []
    lines = content.splitlines()

    # --- Comentarios de Línea ---
    compiled_line_patterns = [re.compile(p) for p in line_comment_patterns]
    for i, line in enumerate(lines):
        for pattern in compiled_line_patterns:
            match = pattern.search(line) # Usar search para encontrar en cualquier parte, no solo al inicio
            if match:
                # Intentar capturar grupo 1, si no, tomar todo después del inicio del comentario
                try:
                    comment_text = match.group(1).strip()
                except IndexError:
                    # Heurística: encontrar dónde empezó el match y tomar el resto
                    start_index = match.start()
                    # Podríamos buscar el delimitador real (ej. '#', '//')
                    comment_text = line[start_index:].lstrip('#/ \t').strip() # Simple fallback

                comments.append({'line': i + 1, 'text': comment_text})
                # Podríamos añadir 'break' si un tipo de comentario excluye otros en la misma línea

    # --- Comentarios de Bloque (Básico) ---
    # Nota: Esto es muy simplificado y no maneja anidamiento ni comentarios dentro de strings.
    # Para lenguajes complejos (JS, Python), es mejor usar tokenizers/parsers específicos.
    current_pos = 0
    for start_pattern_str, end_pattern_str in block_comment_patterns:
        try:
            # Usar re.DOTALL para que '.' coincida con saltos de línea
            block_regex = re.compile(re.escape(start_pattern_str) + r'(.*?)' + re.escape(end_pattern_str), re.DOTALL)
            for match in block_regex.finditer(content):
                 # Calcular línea aproximada (podría ser inexacto)
                 line_approx = content.count('\n', 0, match.start()) + 1
                 text = match.group(1).strip()
                 comments.append({'line': f'block~{line_approx}', 'text': text})
        except Exception as e:
             logger.warning("Error compilando/ejecutando regex de comentario de bloque (%s, %s): %s",
                            start_pattern_str, end_pattern_str, e)

    # Ordenar por línea (aproximada para bloques)
    def sort_key(comment):
        line = comment['line']
        if isinstance(line, str) and line.startswith('block~'):
            try: return int(line.split('~')[1])
            except: return float('inf') # Poner bloques sin línea al final
        elif isinstance(line, int):
            return line
        return float('inf') # Poner 'unknown' al final

    comments.sort(key=sort_key)
    return comments

# --- Función para contar líneas en blanco ---
def count_blank_lines(content: str) -> int:
    """Cuenta las líneas que están vacías o contienen solo espacios en blanco."""
    count = 0
    for line in content.splitlines():
        if not line.strip():
            count += 1
    return count