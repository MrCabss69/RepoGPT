import json
import logging
from typing import Any, Dict
import argparse # Importar argparse

from .base import Reporter
# Asegúrate de importar la excepción si no está ya
from repogpt.exceptions import ReportingError

logger = logging.getLogger(__name__)

class JsonReporter(Reporter):
    """Genera el reporte en formato JSON."""

    # Actualizar firma para aceptar report_options (args) aunque no los usemos aquí
    def generate(self, analysis_data: Dict[str, Any], report_options: argparse.Namespace) -> str:
        """Convierte los datos de análisis a una cadena JSON formateada."""
        logger.info("Generando reporte en formato JSON...")
        # Nota: Las opciones de filtrado (--summary, etc.) no se aplican al formato JSON.
        # El JSON siempre contendrá toda la información extraída.
        if report_options.summary or report_options.dependencies or report_options.tasks or report_options.file_metadata:
             logger.debug("Las opciones de filtrado de secciones no aplican al formato JSON.")

        try:
            report_content = json.dumps(analysis_data, indent=2, ensure_ascii=False, default=str)
            logger.info("Reporte JSON generado exitosamente.")
            return report_content
        except TypeError as e:
            logger.error("Error de serialización JSON: %s. Puede haber tipos de datos no serializables.", e)
            try:
                logger.warning("Intentando serialización JSON con conversión a string por defecto.")
                report_content = json.dumps(analysis_data, indent=2, ensure_ascii=False, default=str)
                return report_content
            except Exception as final_e:
                 logger.critical("Fallo final al generar reporte JSON: %s", final_e, exc_info=True)
                 raise ReportingError(f"No se pudo serializar a JSON: {final_e}") from final_e
        except Exception as e:
             logger.critical("Error inesperado generando reporte JSON: %s", e, exc_info=True)
             raise ReportingError(f"Error inesperado en JsonReporter: {e}") from e