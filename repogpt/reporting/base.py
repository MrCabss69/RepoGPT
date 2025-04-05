# repogpt/reporting/base.py

import abc
from typing import Any, Dict

class Reporter(abc.ABC):
    """Clase base abstracta para generadores de reportes."""

    @abc.abstractmethod
    def generate(self, analysis_data: Dict[str, Any]) -> str:
        """
        Genera el contenido del reporte a partir de los datos analizados.

        Args:
            analysis_data: El diccionario completo que contiene todos los datos
                           recopilados por el analizador y los extractores.

        Returns:
            Una cadena de texto que representa el reporte formateado.
        """
        pass