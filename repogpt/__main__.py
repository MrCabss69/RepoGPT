# repogpt/__main__.py
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Union, Any

from repogpt.analyzer import RepositoryAnalyzer
from repogpt.utils.logging import configure_logging
from repogpt.extractors import base as extractor_base
# Asegúrate de que los extractores que necesitas estén aquí
from repogpt.extractors import dependencies, git, metrics, todos
from repogpt.reporting import base as reporter_base
from repogpt.reporting import json_reporter, markdown_reporter
from repogpt.exceptions import RepoGPTException # Importar excepción

logger = logging.getLogger(__name__)

# Extractores disponibles (puedes ajustar según sea necesario)
AVAILABLE_EXTRACTORS = {
    "dependencies": dependencies.DependencyExtractor,
    "git": git.GitInfoExtractor,
    "metrics": metrics.CodeMetricsExtractor,
    "todos": todos.TodoFixmeExtractor,
}

AVAILABLE_REPORTERS = {
    "json": json_reporter.JsonReporter,
    "md": markdown_reporter.MarkdownReporter,
}

def main():
    parser = argparse.ArgumentParser(
        description="RepoGPT: Analiza y resume repositorios de código para LLMs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        type=Path,
        help="Ruta al repositorio a analizar."
    )
    parser.add_argument(
        "--start-path",
        default="",
        type=str,
        help="Subdirectorio relativo dentro del repositorio para iniciar el análisis."
    )
    parser.add_argument(
        "--output-file",
        "-o",
        default=None,
        type=Path,
        help="Archivo para guardar el reporte. Si no se especifica, se imprime en consola."
    )
    parser.add_argument(
        "--format",
        "-f",
        default="md", # Cambiado a Markdown por defecto, más útil para la estructura
        choices=AVAILABLE_REPORTERS.keys(),
        help="Formato del reporte de salida."
    )
    # Default extractors: quitar los que no sean esenciales para la estructura base
    # 'dependencies', 'git', 'metrics' son necesarios para las secciones opcionales
    # 'todos' es necesario para el conteo por archivo y la sección opcional
    parser.add_argument(
        "--extractors",
        default=",".join(AVAILABLE_EXTRACTORS.keys()), # Mantener todos por ahora
        help=(f"Extractores a usar, separados por coma. "
              f"Disponibles: {', '.join(AVAILABLE_EXTRACTORS.keys())}")
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Número máximo de hilos para procesar archivos."
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=2 * 1024 * 1024, # 2MB
        help="Tamaño máximo de archivo a procesar en bytes."
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="No usar el archivo .gitignore para excluir archivos."
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Nivel de detalle del log."
    )
    parser.add_argument(
        "--version",
        action="version",
        version="RepoGPT 0.3.0" # Actualizar versión
    )

    # --- Nuevos Flags para Secciones Opcionales del Reporte ---
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Incluir la sección de resumen (Git, Métricas) en el reporte."
    )
    parser.add_argument(
        "--dependencies",
        action="store_true",
        default=False,
        help="Incluir la sección detallada de dependencias en el reporte."
    )
    parser.add_argument(
        "--tasks",
        action="store_true",
        default=False,
        help="Incluir la lista agregada de tareas (TODOs/FIXMEs) en el reporte."
    )
    parser.add_argument(
        "--file-metadata",
        action="store_true",
        default=False,
        help="Incluir metadatos detallados (tamaño, hash) por archivo en el reporte."
    )
    # --- Fin Nuevos Flags ---

    args = parser.parse_args()

    try:
        configure_logging(args.log_level)
    except ValueError as e:
        print(f"Error de configuración: {e}")
        exit(1)

    logger.info("Iniciando RepoGPT con configuración: %s", args)

    # --- Selección de Extractores ---
    selected_extractor_names = [name.strip().lower() for name in args.extractors.split(',') if name.strip()]
    selected_extractor_instances: List[extractor_base.ExtractorModule] = []

    # Forzar la inclusión de extractores si sus secciones de reporte son requeridas,
    # incluso si el usuario no los especificó explícitamente en --extractors.
    required_extractors = set()
    if args.summary:
        required_extractors.add("git")
        required_extractors.add("metrics")
    if args.dependencies:
        required_extractors.add("dependencies")
    if args.tasks:
        required_extractors.add("todos")
    # 'todos' también es necesario para el conteo por archivo (comportamiento por defecto)
    required_extractors.add("todos")
    # 'dependencies' también es necesario para la lista simple (comportamiento por defecto)
    required_extractors.add("dependencies")


    final_extractor_names = set(selected_extractor_names) | required_extractors
    missing_required = required_extractors - set(AVAILABLE_EXTRACTORS.keys())
    if missing_required:
        logger.error("Se requieren los extractores %s para las opciones de reporte seleccionadas, pero no están disponibles.", missing_required)
        exit(1)

    for name in final_extractor_names:
        if name in AVAILABLE_EXTRACTORS:
            selected_extractor_instances.append(AVAILABLE_EXTRACTORS[name]())
            logger.debug("Extractor '%s' seleccionado.", name)
        elif name in selected_extractor_names: # Solo advertir si fue explícitamente pedido y no existe
             logger.warning("Extractor '%s' no reconocido. Ignorando.", name)

    if not selected_extractor_instances:
        logger.warning("No se seleccionó ningún extractor válido. El reporte puede estar vacío.")
        # No salimos, podríamos querer un reporte solo con la estructura base.
        # exit(1)

    # --- Selección de Reporter ---
    reporter_class = AVAILABLE_REPORTERS.get(args.format.lower())
    if not reporter_class:
        logger.error("Formato de reporte '%s' no válido. Abortando.", args.format)
        exit(1)
    reporter: reporter_base.Reporter = reporter_class()
    logger.debug("Usando reporter: %s", reporter.__class__.__name__)

    try:
        analyzer = RepositoryAnalyzer(
            repo_path=args.repo_path,
            start_path=args.start_path,
            max_workers=args.max_workers,
            max_file_size=args.max_file_size,
            use_gitignore=not args.no_gitignore,
        )

        # 1. Analizar la estructura y contenido de los archivos
        file_analysis_data = analyzer.analyze_repository()
        logger.info("Análisis de archivos completado.")

        # 2. Ejecutar extractores adicionales
        combined_data = {"files": file_analysis_data}
        for extractor in selected_extractor_instances:
             logger.debug("Ejecutando extractor: %s", extractor.__class__.__name__)
             try:
                 extracted_data = extractor.extract(analyzer, combined_data)
                 # Asegurarse de que la clave principal exista antes de actualizar
                 if extracted_data:
                      combined_data.update(extracted_data)
             except Exception as e:
                 extractor_name = extractor.__class__.__name__
                 logger.error("Error ejecutando extractor %s: %s", extractor_name, e, exc_info=True)
                 # Usar una clave de error más específica
                 if "errors" not in combined_data: combined_data["errors"] = {}
                 if "extractors" not in combined_data["errors"]: combined_data["errors"]["extractors"] = {}
                 combined_data["errors"]["extractors"][extractor_name] = str(e)


        logger.info("Extracción de información adicional completada.")

        # 3. Generar el reporte, pasando las opciones (args)
        # Verificar si el reporter acepta las opciones
        import inspect
        sig = inspect.signature(reporter.generate)
        if len(sig.parameters) > 1: # Si acepta más que 'self' y 'analysis_data'
            report_content = reporter.generate(combined_data, args)
        else:
             # Reporter antiguo o no soporta opciones (ej. JSONReporter)
             report_content = reporter.generate(combined_data)
             if args.summary or args.dependencies or args.tasks or args.file_metadata:
                   logger.warning("El reporter %s no soporta opciones de filtrado (--summary, etc.). Se incluirá toda la información.", reporter.__class__.__name__)

        logger.info("Generación de reporte completada.")

        # 4. Guardar o imprimir
        if args.output_file:
            try:
                args.output_file.parent.mkdir(parents=True, exist_ok=True)
                with args.output_file.open("w", encoding="utf-8") as f:
                    f.write(report_content)
                logger.info("Reporte guardado en: %s", args.output_file)
                print(f"Reporte guardado en: {args.output_file}")
            except IOError as e:
                logger.error("No se pudo escribir el archivo de salida %s: %s", args.output_file, e)
                # Imprimir si falla el guardado, pero ahora el reporte puede ser muy largo
                print(f"\n--- Reporte ({args.format}) ---")
                print("Error al guardar, imprimiendo las primeras 50 líneas:")
                print("\n".join(report_content.splitlines()[:50]))
                if len(report_content.splitlines()) > 50: print("[... truncado ...]")

        else:
            print(report_content)

    except (FileNotFoundError, NotADirectoryError, ValueError, RepoGPTException) as e: # Añadir RepoGPTException
         logger.error("Error de configuración o análisis: %s", e, exc_info=True)
         print(f"Error: {e}")
         exit(1)
    except Exception as e:
        logger.critical("Error inesperado durante la ejecución: %s", e, exc_info=True)
        print(f"Error inesperado: {e}")
        exit(1)

if __name__ == "__main__":
    main()