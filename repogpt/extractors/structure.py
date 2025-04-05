# repogpt/extractors/structure.py
import logging
from pathlib import Path
from typing import Any, Dict, List

from .base import ExtractorModule
from repogpt.analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)

class StructureExtractor(ExtractorModule):
    """Extrae una visión general de la estructura (clases, funciones) por archivo."""

    def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Itera sobre los archivos analizados y extrae elementos estructurales clave."""
        logger.info("Extrayendo resumen de estructura...")
        structure_summary: Dict[str, Dict[str, List[str]]] = {}

        files_data = analyzed_data.get("files", {})
        if not files_data:
            logger.warning("No hay datos de archivos ('files') para extraer estructura.")
            return {"structure_summary": structure_summary}

        for relative_path, file_info in files_data.items():
            if not isinstance(file_info, dict) or '_error' in file_info:
                continue 

            file_structure: Dict[str, List[str]] = {}

            # Extraer nombres de clases
            if classes := file_info.get('classes'):
                if isinstance(classes, list):
                    # Asumiendo que cada item de 'classes' es un dict con 'name'
                    file_structure['classes'] = [c.get('name', 'N/A') for c in classes if isinstance(c, dict)]

            # Extraer nombres de funciones (a nivel de módulo)
            if functions := file_info.get('functions'):
                 if isinstance(functions, list):
                    # Asumiendo que cada item de 'functions' es un dict con 'name'
                     file_structure['functions'] = [f.get('name', 'N/A') for f in functions if isinstance(f, dict)]

            # Extraer nombres de componentes (de JS/TS)
            if components := file_info.get('components'):
                 if isinstance(components, list):
                    file_structure['components'] = [str(comp) for comp in components] # Asegurar que sean strings

            # Extraer exports (de JS/TS)
            if exports := file_info.get('exports'):
                 if isinstance(exports, list):
                    file_structure['exports'] = [str(exp) for exp in exports]

            # Añadir otros elementos si los parsers los proporcionan (ej. 'interfaces' de TS)

            if file_structure: # Solo añadir si se encontró algo
                 structure_summary[relative_path] = file_structure
                 logger.debug("Estructura extraída para: %s", relative_path)

        logger.info("Resumen de estructura generado para %d archivos.", len(structure_summary))
        return {"structure_summary": structure_summary}