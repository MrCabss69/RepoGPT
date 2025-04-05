# repogpt/utils/gitignore_handler.py
import logging
from pathlib import Path
from typing import Callable, Optional, Dict

# Importar la librería
try:
    # Importar la función específica directamente
    from gitignore_parser import parse_gitignore as gitignore_parse_function
    gitignore_parser_available = True
    # print(f"DEBUG: Importing gitignore_parser function") # Mantener si aún se necesita depurar
except ImportError:
    gitignore_parse_function = None
    gitignore_parser_available = False
    logging.warning("gitignore-parser no instalado. El manejo de .gitignore será limitado o inexistente.")
    logging.warning("Instala con: pip install gitignore-parser")

logger = logging.getLogger(__name__)

# Variable global para cachear el matcher (opcional, pero puede mejorar rendimiento)
_cached_matchers: Dict[Path, Optional[Callable[[str], bool]]] = {}

def _load_matcher_uncached(gitignore_path: Path) -> Optional[Callable[[str], bool]]:
    """Carga el matcher desde un archivo .gitignore sin usar caché."""
    if not gitignore_path.is_file():
        logger.debug(".gitignore no encontrado en %s", gitignore_path)
        return None

    if not gitignore_parser_available or gitignore_parse_function is None:
        logger.warning("gitignore-parser o su función parse_gitignore no están disponibles, no se puede parsear %s", gitignore_path)
        return None # No podemos hacer matching

    try:
        # --- CAMBIO CLAVE: Usar la función correcta 'parse_gitignore' y pasar la ruta ---
        matcher = gitignore_parse_function(gitignore_path)
        # ---------------------------------------------------------------------------

        if matcher: # Asegurarse de que la función devolvió algo usable
             logger.info("Matcher de .gitignore cargado desde %s", gitignore_path)
             return matcher
        else:
            # Esto no debería pasar si parse_gitignore tiene éxito, pero por si acaso
             logger.warning("gitignore_parse_function devolvió None o False para %s", gitignore_path)
             return None

    except Exception as e:
        # Capturar cualquier otro error durante el parseo del gitignore
        logger.error("Error ejecutando parse_gitignore en %s: %s", gitignore_path, e, exc_info=True)
        return None # Error al parsear, tratar como si no hubiera gitignore

def get_gitignore_matcher(repo_path: Path, use_cache: bool = True) -> Optional[Callable[[str], bool]]:
    """
    Obtiene la función matcher para el .gitignore del repositorio, opcionalmente desde caché.

    Args:
        repo_path: La ruta raíz del repositorio donde buscar .gitignore.
        use_cache: Si se debe usar la caché de matchers.

    Returns:
        Una función que toma un path (string) y devuelve True si debe ser ignorado,
        o None si no hay .gitignore o no se pudo parsear.
    """
    gitignore_path = repo_path / ".gitignore"

    if use_cache:
        if gitignore_path in _cached_matchers:
            logger.debug("Usando matcher de .gitignore cacheado para %s", gitignore_path)
            return _cached_matchers[gitignore_path]
        else:
            matcher = _load_matcher_uncached(gitignore_path)
            _cached_matchers[gitignore_path] = matcher
            return matcher
    else:
        # Forzar recarga si no se usa caché
        return _load_matcher_uncached(gitignore_path)

def is_path_ignored(absolute_path: Path, matcher: Optional[Callable[[str], bool]]) -> bool:
    """
    Verifica si una ruta absoluta debe ser ignorada según el matcher de .gitignore.

    Args:
        absolute_path: La ruta absoluta del archivo o directorio a verificar.
        matcher: La función matcher obtenida de get_gitignore_matcher.

    Returns:
        True si la ruta debe ser ignorada, False en caso contrario.
    """
    if matcher is None:
        return False # No hay matcher, no ignorar

    try:
        # La librería espera un path string absoluto según el ejemplo
        # Asegurarse de que el path sea absoluto
        path_str = str(absolute_path.resolve())
        is_ignored = matcher(path_str)
        if is_ignored:
             logger.debug("Ruta %s ignorada por .gitignore.", path_str)
        return is_ignored
    except Exception as e:
         # Captura errores inesperados del matcher
         logger.error("Error aplicando matcher de gitignore a %s: %s", absolute_path, e, exc_info=True)
         return False # Mejor no ignorar si hay error en el matcher