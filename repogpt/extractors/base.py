# repogpt/extractors/base.py

import abc
import logging
from typing import Any, Dict

# Importar la clase principal para type hints si es necesario (evitando importación circular)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from repogpt.analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)

class ExtractorModule(abc.ABC):
    """Clase base abstracta para módulos que extraen información específica."""

    @abc.abstractmethod
    def extract(self, analyzer: 'RepositoryAnalyzer', analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae información específica del repositorio o de los datos ya analizados.

        Args:
            analyzer: La instancia de RepositoryAnalyzer (para acceso a repo_path, etc.).
            analyzed_data: El diccionario que contiene los resultados del análisis
                           de archivos realizado por RepositoryAnalyzer (bajo la clave 'files').
                           Este diccionario puede ser modificado por extractores anteriores.

        Returns:
            Un diccionario que contiene la información extraída. La clave principal
            debe ser única para este extractor (ej. 'dependencies', 'git_info').
            Este diccionario se fusionará con los resultados generales.
            Debe devolver un diccionario vacío ({}) si no se extrae nada.
        """
        pass