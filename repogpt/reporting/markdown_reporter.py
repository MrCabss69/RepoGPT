# repogpt/reporting/markdown_reporter.py

import logging
from typing import Any, Dict, List
import json
import argparse

from .base import Reporter

logger = logging.getLogger(__name__)

class MarkdownReporter(Reporter):
    """Genera el reporte en formato Markdown, incluyendo estructura detallada del código."""

    # El método generate ahora acepta 'report_options' (que será args)
    def generate(self, analysis_data: Dict[str, Any], report_options: argparse.Namespace) -> str:
        """Crea una cadena de texto Markdown a partir de los datos de análisis."""
        logger.info("Generando reporte Markdown con opciones: %s", report_options)
        report_lines: List[str] = ["# RepoGPT Analysis Report"]

        # --- 1. Resumen General (Opcional) ---
        if report_options.summary:
            report_lines.append("\n## Summary\n")
            git_info = analysis_data.get("git_info")
            metrics = analysis_data.get("code_metrics")

            if git_info:
                report_lines.append("### Git Information")
                report_lines.append(f"- **Branch:** `{git_info.get('branch', 'N/A')}`")
                report_lines.append(f"- **Commit:** `{git_info.get('commit_short_hash', 'N/A')}`")
                report_lines.append(f"- **Author:** {git_info.get('author_name', 'N/A')}")
                report_lines.append(f"- **Date:** {git_info.get('commit_date', 'N/A')}")
                if tags := git_info.get('tags'):
                    report_lines.append(f"- **Tags:** {', '.join(f'`{t}`' for t in tags)}")
                report_lines.append("")
            elif report_options.summary: # Si se pidió summary pero no hay datos git
                 report_lines.append("*(Git information not available or extractor disabled)*\n")


            if metrics:
                report_lines.append("### Code Metrics")
                report_lines.append(f"- **Total Files Analyzed:** {metrics.get('total_files', 0)}")
                report_lines.append(f"- **Total Lines:** {metrics.get('total_lines', 0)}")
                report_lines.append(f"- **Code Lines:** {metrics.get('code_lines', 0)}")
                report_lines.append(f"- **Comment Lines:** {metrics.get('total_comment_lines', 0)}")
                report_lines.append(f"- **Blank Lines:** {metrics.get('total_blank_lines', 0)}")
                report_lines.append(f"- **Total Size:** {self._format_size(metrics.get('total_size_bytes', 0))}")
                
                report_lines.append(f"- **Files with Errors:** {metrics.get('files_with_errors', 0)}")
                if metrics.get('files_missing_line_data', 0) > 0:
                    report_lines.append(f"- **Files without Line Data:** {metrics['files_missing_line_data']}")
                if ext_stats := metrics.get("files_by_extension"):
                    report_lines.append("- **File Types:**")
                    report_lines.append("  | Extension | Count |")
                report_lines.append("")
            elif report_options.summary: # Si se pidió summary pero no hay datos de métricas
                 report_lines.append("*(Code metrics not available or extractor disabled)*\n")


        # --- 2. Dependencias (Simple por defecto, Detallado opcional) ---
        dependencies_data = analysis_data.get("dependencies")
        if dependencies_data:
             if report_options.dependencies:
                 report_lines.append("\n## Dependencies (Detailed)\n")
                 for file_name, deps in sorted(dependencies_data.items()):
                     report_lines.append(f"### `{file_name}`")
                     if isinstance(deps, dict) and '_error' in deps:
                         report_lines.append(f"  - **Error parsing:** {deps['_error']}")
                     elif isinstance(deps, list) and deps and isinstance(deps[0], dict) and '_error' in deps[0]:
                          report_lines.append(f"  - **Error parsing:** {deps[0]['_error']}")
                     elif isinstance(deps, dict) or isinstance(deps, list):
                         try:
                              deps_str = json.dumps(deps, indent=2, ensure_ascii=False)
                              report_lines.append(f"```json\n{deps_str}\n```")
                         except TypeError:
                              report_lines.append(f"```\n{str(deps)}\n```")
                     else:
                         report_lines.append("  - *No dependencies found or unrecognized format.*")
                     report_lines.append("")
             # Comportamiento Simple (por defecto, si hay datos pero no se pide detalle)
             elif not report_options.dependencies:
                  detected_files = [f"`{fname}`" for fname, data in dependencies_data.items() if not (isinstance(data, dict) and '_error' in data)]
                  if detected_files:
                      report_lines.append("\n## Dependencies Found\n")
                      report_lines.append(f"- Files: {', '.join(detected_files)}")
                      report_lines.append("  *(Run with `--dependencies` for details)*")
                      report_lines.append("")

        # --- 3. Tareas Pendientes (Lista agregada opcional) ---
        tasks_data = analysis_data.get("aggregated_tasks")
        if tasks_data and report_options.tasks: # Solo mostrar si hay datos Y se pidió con --tasks
            total_todos = tasks_data.get("total_todos", 0)
            total_fixmes = tasks_data.get("total_fixmes", 0)
            if total_todos > 0 or total_fixmes > 0:
                report_lines.append(f"\n## Aggregated Tasks ({total_todos} TODOs, {total_fixmes} FIXMEs)\n")
                if todos_map := tasks_data.get("todos"):
                     self._append_task_section(report_lines, "TODOs", todos_map)
                if fixmes_map := tasks_data.get("fixmes"):
                     self._append_task_section(report_lines, "FIXMEs", fixmes_map)

        # --- 4. Detalles por Archivo (Metadata detallada opcional, conteo de tareas por defecto) ---
        if files_data := analysis_data.get("files"):
            report_lines.append("\n## File Details\n")
            sorted_files = sorted(files_data.items())
            # Obtener datos de tareas agregadas para los conteos por archivo
            aggregated_tasks = analysis_data.get("aggregated_tasks", {})
            todos_by_file = aggregated_tasks.get("todos", {})
            fixmes_by_file = aggregated_tasks.get("fixmes", {})


            for relative_path, file_info in sorted_files:
                if not isinstance(file_info, dict):
                    continue

                report_lines.append(f"### `{relative_path}`")

                # Metadata: Líneas siempre, resto opcional
                if 'line_count' in file_info:
                     report_lines.append(f"- **Lines:** {file_info['line_count']}")
                if report_options.file_metadata:
                    report_lines.append(f"- **Size:** {self._format_size(file_info.get('size', 0))}")
                    report_lines.append(f"- **Hash (SHA256):** `{file_info.get('hash', 'N/A')}`")

                # Conteo de Tareas por Archivo (siempre, si existen)
                num_todos = len(todos_by_file.get(relative_path, []))
                num_fixmes = len(fixmes_by_file.get(relative_path, []))
                if num_todos > 0 or num_fixmes > 0:
                    task_summary = []
                    if num_todos > 0:
                        task_summary.append(f"{num_todos} TODOs")
                    if num_fixmes > 0:
                        task_summary.append(f"{num_fixmes} FIXMEs")
                    report_lines.append(f"- **Tasks Found:** {', '.join(task_summary)}")
                    # Añadir nota si la lista completa no está visible
                    if not report_options.tasks:
                         report_lines.append("  *(Run with `--tasks` for full list)*")


                if error := file_info.get('_error'):
                    report_lines.append(f"- **<span style='color:red;'>Error:</span>** `{error}`")
                    if structure := file_info.get('structure'):
                        if structure:
                             report_lines.append("\n#### Partial Structure (before error):")
                             self._render_structure(report_lines, structure, indent_level=0)
                    report_lines.append("\n---\n")
                    continue

                # Renderizar Estructura Ordenada (siempre)
                if structure := file_info.get('structure'):
                    report_lines.append("\n#### Structure:")
                    if not structure:
                        report_lines.append("\n*No significant structure found.*")
                    else:
                        self._render_structure(report_lines, structure, indent_level=0)
                else:
                    report_lines.append("\n*Structure information not available for this file type or parsing failed early.*")

                # Otros datos específicos del parser (menos relevantes, quizás ocultar por defecto?)
                if base_images := file_info.get('base_images'):
                    img_strs = [f"`{img.get('image', 'N/A')}{':' + img.get('tag', '') if img.get('tag') else ''}{'@' + img.get('digest', '') if img.get('digest') else ''}{' as ' + img.get('alias', '') if img.get('alias') else ''}`" for img in base_images]
                    report_lines.append(f"- **(Dockerfile) Base Images:** {', '.join(img_strs)}")
                if exposed_ports := file_info.get('exposed_ports'):
                    report_lines.append(f"- **(Dockerfile) Exposed Ports:** {', '.join(f'`{p}`' for p in exposed_ports)}")


                report_lines.append("\n---\n") # Separador

        # Considerar añadir una nota al final si se usaron filtros
        if not (report_options.summary and report_options.dependencies and report_options.tasks and report_options.file_metadata):
             report_lines.append("\n*Note: Some sections may be hidden. Use flags like `--summary`, `--dependencies`, `--tasks`, `--file-metadata` to show more details.*")

        logger.info("Reporte Markdown generado exitosamente.")
        return "\n".join(report_lines)

    # --- Métodos _render_structure, _render_function, _render_class sin cambios ---
    def _render_structure(self, lines: List[str], structure: List[Dict[str, Any]], indent_level: int = 0):
        """Renderiza recursivamente la lista de elementos estructurales."""
        indent = "  " * indent_level
        for i, element in enumerate(structure):
            elem_type = element.get('type', 'unknown')
            line_start = element.get('line_start', '?')
            if indent_level == 0 and i > 0: 
                lines.append("")
            if elem_type == 'comment':
                lines.append(f"{indent}> *(L{line_start}) {element.get('text', '')}*")
            elif elem_type == 'import':
                lines.append(f"{indent}- *(L{line_start})* Import: `{element.get('value', 'N/A')}`")
            elif elem_type == 'function' or elem_type == 'method':
                self._render_function(lines, element, indent)
            elif elem_type == 'class':
                self._render_class(lines, element, indent, indent_level)
            else:
                lines.append(f"{indent}- *(L{line_start})* **{elem_type.capitalize()}:** `{element.get('name', str(element))}`")

    def _render_function(self, lines: List[str], element: Dict[str, Any], indent: str):
        """Renderiza una función o método."""
        line_start = element.get('line_start', '?')
        name = element.get('name', 'anonymous')
        args = element.get('arguments', [])
        returns = element.get('returns')
        decorators = element.get('decorators', [])
        docstring = element.get('docstring')
        is_async = element.get('is_async', False)
        elem_type = element.get('type', 'function')
        header = f"{elem_type.capitalize()} `{name}`"
        signature = f"({', '.join(args)})"
        if returns: 
            signature += f" -> `{returns}`"
        if is_async:
            header = f"Async {header}"
        lines.append(f"{indent}#### {header} *(L{line_start})*")
        for dec in decorators: 
            lines.append(f"{indent}> Decorator: `{dec}`")
        lines.append(f"{indent}```python\ndef {name}{signature}:\n    ...\n```")
        if docstring:
            lines.append(f"{indent}> **Docstring:**")
            docstring_lines = docstring.strip().split('\n')
            min_indent = float('inf')
            for line in docstring_lines[1:]:
                leading_spaces = len(line) - len(line.lstrip(' '))
                if line.strip(): 
                    min_indent = min(min_indent, leading_spaces)
            if min_indent == float('inf'): 
                min_indent = 0
            formatted_docstring = [docstring_lines[0].strip()]
            formatted_docstring.extend([line[min_indent:] for line in docstring_lines[1:]])
            lines.append(f"{indent}> ```text")
            lines.extend([f"{indent}> {line}" for line in formatted_docstring])
            lines.append(f"{indent}> ```")

    def _render_class(self, lines: List[str], element: Dict[str, Any], indent: str, indent_level: int):
        """Renderiza una clase y su cuerpo."""
        line_start = element.get('line_start', '?')
        name = element.get('name', 'AnonymousClass')
        bases = element.get('bases', [])
        decorators = element.get('decorators', [])
        docstring = element.get('docstring')
        body = element.get('body', [])
        header = f"Class `{name}`"
        if bases: 
            header += f"({', '.join(f'`{b}`' for b in bases)})"
        lines.append(f"{indent}#### {header} *(L{line_start})*")
        for dec in decorators: 
            lines.append(f"{indent}> Decorator: `{dec}`")
        if docstring:
            lines.append(f"{indent}> **Docstring:**")
            docstring_lines = docstring.strip().split('\n')
            min_indent = float('inf')
            for line in docstring_lines[1:]:
                leading_spaces = len(line) - len(line.lstrip(' '))
                if line.strip(): 
                    min_indent = min(min_indent, leading_spaces)
            if min_indent == float('inf'): 
                min_indent = 0
            formatted_docstring = [docstring_lines[0].strip()]
            formatted_docstring.extend([line[min_indent:] for line in docstring_lines[1:]])
            lines.append(f"{indent}> ```text")
            lines.extend([f"{indent}> {line}" for line in formatted_docstring])
            lines.append(f"{indent}> ```")
        if body:
            lines.append(f"{indent}**Body:**")
            self._render_structure(lines, body, indent_level=indent_level + 1)

    # --- Métodos auxiliares _format_size, _append_task_section sin cambios ---
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024: 
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

    # Este método ahora solo se usa si se pide --tasks
    def _append_task_section(self, lines: List[str], title: str, task_map: Dict[str, List[Dict[str, Any]]]):
        lines.append(f"#### {title}")
        if not task_map:
            lines.append(f"- *No {title} found.*")
            lines.append("")
            return
        for file_path, tasks in sorted(task_map.items()):
            lines.append(f"- `{file_path}`:")
            for task in tasks:
                line_num = task.get('line', '?')
                message = task.get('message', 'No message')
                lines.append(f"  - (L{line_num}) {message}")
        lines.append("")