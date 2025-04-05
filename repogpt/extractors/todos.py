# repogpt/extractors/todos.py
import logging
from typing import Any, Dict, List

from .base import ExtractorModule
from repogpt.analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)

class TodoFixmeExtractor(ExtractorModule):
    """Agrega todos los TODOs y FIXMEs encontrados por los parsers."""

    def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recopila las entradas 'todos_fixmes' de cada archivo analizado."""
        logger.info("Agregando TODOs y FIXMEs...")
        aggregated_todos: Dict[str, List[Dict[str, Any]]] = {}
        aggregated_fixmes: Dict[str, List[Dict[str, Any]]] = {}
        total_todos = 0
        total_fixmes = 0

        files_data = analyzed_data.get("files", {})
        if not files_data:
            logger.warning("No hay datos de archivos ('files') para agregar TODOs/FIXMEs.")
            return {"aggregated_tasks": {"todos": {}, "fixmes": {}}}

        for relative_path, file_info in files_data.items():
            if not isinstance(file_info, dict) or '_error' in file_info:
                continue

            if todos_fixmes := file_info.get('todos_fixmes'):
                if isinstance(todos_fixmes, dict):
                    if todos_list := todos_fixmes.get('todos'):
                        if isinstance(todos_list, list) and todos_list:
                            aggregated_todos[relative_path] = todos_list
                            total_todos += len(todos_list)
                    if fixmes_list := todos_fixmes.get('fixmes'):
                         if isinstance(fixmes_list, list) and fixmes_list:
                            aggregated_fixmes[relative_path] = fixmes_list
                            total_fixmes += len(fixmes_list)

        logger.info("Agregación completada: %d TODOs, %d FIXMEs encontrados.", total_todos, total_fixmes)
        return {
            "aggregated_tasks": {
                "todos": aggregated_todos,
                "fixmes": aggregated_fixmes,
                "total_todos": total_todos,
                "total_fixmes": total_fixmes
            }
        }