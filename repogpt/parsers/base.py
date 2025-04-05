# repogpt/parsers/base.py

import abc
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

# *** NO IMPORTAR dockerfile NI generic AQUÍ ARRIBA ***
from ..utils.file_utils import is_likely_binary

logger = logging.getLogger(__name__)


# --- Interfaz Base del Parser ---
class Parser(abc.ABC):
    """Clase base abstracta para todos los parsers de archivos."""

    @abc.abstractmethod
    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza el contenido del archivo dado.

        Args:
            file_path: Ruta al archivo a analizar.
            file_info: Diccionario con metadatos pre-calculados (size, hash, etc.).
                       El parser puede añadir o modificar este diccionario.

        Returns:
            Un diccionario con la información extraída específica del tipo de archivo.
            Este diccionario será fusionado con file_info.
            Debe devolver un diccionario vacío ({}) si no hay nada específico que extraer.
            Puede lanzar excepciones si el parsing falla catastróficamente,
            aunque es preferible devolver {'error': 'mensaje'} si es posible.
        """
        pass

# --- Registro de Parsers ---
# Mapea extensiones de archivo (en minúsculas) a la clase Parser correspondiente.
_parser_registry: Dict[str, Type[Parser]] = {}
def register_parser(extension: str, parser_class: Type[Parser]) -> None:
    """Registra una clase Parser para una extensión de archivo específica."""
    if not extension.startswith('.'):
        logger.warning("La extensión '%s' no empieza con '.', podría causar problemas.", extension)

    ext_lower = extension.lower()
    if ext_lower in _parser_registry:
        logger.warning("Extensión '%s' ya registrada con %s. Sobrescribiendo con %s.",
                       ext_lower, _parser_registry[ext_lower].__name__, parser_class.__name__)

    if not issubclass(parser_class, Parser):
         raise TypeError(f"La clase {parser_class.__name__} debe heredar de Parser.")

    _parser_registry[ext_lower] = parser_class
    logger.debug("Parser %s registrado para la extensión %s", parser_class.__name__, ext_lower)
    
# --- Función Principal get_parser ---
def get_parser(file_path: Path) -> Optional[Parser]:
    """
    Obtiene una instancia del parser adecuado para el archivo.
    Prioriza el nombre de archivo 'Dockerfile' y luego la extensión.

    Args:
        file_path: Ruta al archivo.

    Returns:
        Una instancia del Parser registrado, o None si no hay parser adecuado.
    """
    filename = file_path.name
    extension = file_path.suffix.lower()
    parser_class: Optional[Type[Parser]] = None

    # --- Comprobación Especial por Nombre de Archivo ---
    if filename.lower() == 'dockerfile':
        # Buscar la clase DockerfileParser por su nombre o una clave especial
        # Asumimos que DockerfileParser se registró con alguna extensión (ej. .dockerfile)
        # o podríamos buscarla explícitamente por nombre de clase si fuera necesario.
        # Lo más simple es buscarla si está registrada bajo '.dockerfile'
        parser_class = _parser_registry.get('.dockerfile') # Buscar por la extensión registrada
        if parser_class:
            logger.debug("Detectado archivo por nombre 'Dockerfile', usando parser registrado para '.dockerfile': %s", file_path)
        else:
            # Si no se registró con .dockerfile, necesitaríamos otro mecanismo
            # Podríamos importar dinámicamente o buscar en globals() pero es más complejo.
            # Por ahora, asumimos que debe registrarse con .dockerfile.
            logger.warning("Archivo llamado 'Dockerfile' encontrado, pero ningún parser está registrado para la extensión '.dockerfile'.")


    # --- Comprobación por Extensión (si no se encontró por nombre 'Dockerfile') ---
    if parser_class is None and extension:
        parser_class = _parser_registry.get(extension)
        if parser_class:
             logger.debug("Parser %s encontrado por extensión '%s' para %s",
                          parser_class.__name__, extension, file_path)
        # else: # Log ya hecho si se buscó por extensión
        #     logger.debug("No se encontró parser registrado para la extensión '%s' de %s",
        #                  extension, file_path)


    # --- Fallback a GenericTextParser ---
    if parser_class is None:
        if not is_likely_binary(file_path):
            try:
                # Importar generic aquí dentro
                from . import generic
                parser_class = generic.GenericTextParser
                logger.debug("No se encontró parser específico para %s y no parece binario. Usando GenericTextParser.", file_path)
            except ImportError:
                logger.error("No se pudo importar GenericTextParser. Fallback no disponible.")
        else:
             logger.debug("Archivo %s parece binario y no tiene parser específico. Omitiendo parsing.", file_path)

    # --- Instanciación ---
    if parser_class:
        try:
            return parser_class()
        except Exception as e:
             logger.error("Error instanciando parser %s: %s", parser_class.__name__, e, exc_info=True)
             return None
    else:
        return None
    
# --- Importación dinámica o registro explícito ---
# Ahora, en cada archivo de parser específico (ej. repogpt/parsers/python.py), harías algo como:
#
# from .base import Parser, register_parser
# import ast
#
# class PythonParser(Parser):
#     def parse(self, file_path, file_info):
#         # ... lógica de parsing con AST ...
#         content = file_path.read_text(...)
#         # ...
#         return {'classes': [...], 'functions': [...]}
#
# # Registrar el parser al importar el módulo
# register_parser('.py', PythonParser)

# Para que esto funcione, necesitarías importar todos los módulos de parser
# en algún punto central, por ejemplo, en repogpt/parsers/__init__.py:
#
# # repogpt/parsers/__init__.py
# from . import python
# from . import markdown
# from . import javascript
# # ... etc. para todos los parsers que crees
#
# from .base import get_parser # Re-exportar la función principal si se desea