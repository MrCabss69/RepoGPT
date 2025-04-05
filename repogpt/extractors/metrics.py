# repogpt/extractors/metrics.py
import logging
from pathlib import Path
from typing import Any, Dict

from .base import ExtractorModule
from repogpt.analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)

class CodeMetricsExtractor(ExtractorModule):
    """Calcula métricas básicas del código analizado."""

    def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula totales y estadísticas por tipo de archivo."""
        logger.info("Calculando métricas de código...")
        metrics: Dict[str, Any] = {
            "total_files": 0,
            "total_lines": 0,
            "total_size_bytes": 0,
            "total_comment_lines": 0, # Renombrado para claridad
            "total_blank_lines": 0,
            "code_lines": 0, # Calculado al final
            "files_by_extension": {},
            "files_with_errors": 0,
            "files_missing_line_data": 0, # Nuevo contador
        }

        files_data = analyzed_data.get("files", {})
        if not files_data:
            logger.warning("No hay datos de archivos ('files') para calcular métricas.")
            return {"code_metrics": metrics}

        for relative_path, file_info in files_data.items():
            if not isinstance(file_info, dict):
                logger.warning("Entrada inesperada en 'files' para '%s', omitiendo métricas.", relative_path)
                continue

            metrics["total_files"] += 1
            metrics["total_size_bytes"] += file_info.get('size', 0)

            # Usar la extensión del path relativo
            ext = Path(relative_path).suffix.lower()
            if not ext:
                ext = "_no_extension_"
            metrics["files_by_extension"][ext] = metrics["files_by_extension"].get(ext, 0) + 1

            if '_error' in file_info:
                metrics["files_with_errors"] += 1
                # No sumar líneas si hubo error, pero verificar si tenemos conteo parcial
                if 'line_count' not in file_info:
                     metrics["files_missing_line_data"] += 1
                # Aún así, sumar el tamaño y contar el archivo por extensión

            # Sumar líneas solo si no hubo error grave y tenemos el conteo
            elif 'line_count' in file_info:
                line_count = file_info['line_count']
                metrics["total_lines"] += line_count

                # Sumar comentarios y líneas en blanco si están disponibles
                comment_count = file_info.get('comments_count', 0)
                blank_count = file_info.get('blank_lines', 0) # Obtener líneas en blanco
                metrics["total_comment_lines"] += comment_count
                metrics["total_blank_lines"] += blank_count

            else:
                # El archivo se procesó pero el parser no devolvió 'line_count'
                 metrics["files_missing_line_data"] += 1


        # Calcular líneas de código al final
        metrics["code_lines"] = (metrics["total_lines"] -
                                 metrics["total_comment_lines"] -
                                 metrics["total_blank_lines"])
        # Asegurarse de que no sea negativo si los contadores son inconsistentes
        metrics["code_lines"] = max(0, metrics["code_lines"])


        log_msg = (f"Métricas calculadas: {metrics['total_files']} archivos, "
                   f"{metrics['total_lines']} líneas totales, "
                   f"{metrics['total_comment_lines']} coment., "
                   f"{metrics['total_blank_lines']} en blanco, "
                   f"~{metrics['code_lines']} código.")
        if metrics['files_missing_line_data'] > 0:
             log_msg += f" ({metrics['files_missing_line_data']} archivos sin datos de líneas)"
        if metrics['files_with_errors'] > 0:
             log_msg += f" ({metrics['files_with_errors']} con errores)"

        logger.info(log_msg)
        return {"code_metrics": metrics}