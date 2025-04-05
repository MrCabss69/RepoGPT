# repogpt/analyzer.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional, Union
import os
import logging
from pathlib import Path

from .parsers.base import get_parser
from .utils.file_utils import calculate_file_hash, is_likely_binary
from .utils.gitignore_handler import get_gitignore_matcher, is_path_ignored


MAX_FILE_SIZE: int = 2 * 1024 * 1024  # 2MB

logger = logging.getLogger(__name__)

class RepositoryAnalyzer:
    def __init__(
        self,
        repo_path: Union[str, Path],
        start_path: str = "",
        max_depth: Optional[int] = None,
        max_workers: int = 4,
        max_file_size: int = MAX_FILE_SIZE,
        use_gitignore: bool = True
    ) -> None:
        self.repo_path = Path(repo_path).resolve()
        self.start_path = (self.repo_path / start_path).resolve()
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.max_file_size = max_file_size
        
        self.gitignore_matcher = get_gitignore_matcher(self.repo_path) if use_gitignore else None

        self._validate_paths()
        logger.info("Analyzer inicializado para: %s", self.start_path)
    def _validate_paths(self) -> None:
        if not self.repo_path.is_dir():
            raise NotADirectoryError(f"Ruta del repositorio no es un directorio: {self.repo_path}")
        if not self.start_path.exists():
            raise FileNotFoundError(f"Ruta inicial no existe: {self.start_path}")
        # Asegurarse que start_path está dentro de repo_path
        try:
            self.start_path.relative_to(self.repo_path)
        except ValueError as e:
            raise ValueError(f"La ruta inicial {self.start_path} no está dentro del repositorio {self.repo_path}")


    def is_excluded(self, path: Path) -> bool:
        # 1. Verificar si está fuera del start_path (no debería pasar con os.walk bien usado)
        try:
            path.relative_to(self.start_path)
        except ValueError:
             logger.warning("Ruta %s fuera de la ruta de inicio %s", path, self.start_path)
             return True

        # 2. Excluir el directorio .git explícitamente
        if ".git" in path.relative_to(self.repo_path).parts:
             logger.debug("Excluido por ser parte de .git: %s", path)
             return True

        # 3. Gitignore (usando la librería)
        if self.gitignore_matcher and is_path_ignored(path, self.gitignore_matcher):
            return True# El log ya se hace dentro de is_path_ignored

        # 4. Detección de Binarios (si es archivo)
        if path.is_file() and is_likely_binary(path):
             logger.debug("Excluido por ser binario probable: %s", path)
             return True

        # 5. (Opcional) Añadir patrones de exclusión adicionales aquí si se reimplementan
        return False

    def _walk_directory(self):
        # Usar os.walk para manejar directorios y archivos de forma estándar
        for root, dirs, files in os.walk(self.start_path, topdown=True):
            current_path = Path(root)
            rel_depth = len(current_path.relative_to(self.start_path).parts)

            # --- Optimización: Filtrar directorios en una nueva lista ---
            valid_dirs = []
            excluded_dirs = [] # Para logging si es necesario
            for d in dirs:
                dir_path = current_path / d
                if self.is_excluded(dir_path):
                    excluded_dirs.append(d)
                    continue
                if self.max_depth is not None and rel_depth >= self.max_depth:
                    excluded_dirs.append(d)
                    logger.debug("Excluyendo directorio por profundidad: %s", dir_path)
                    continue
                valid_dirs.append(d)

            # Modificar dirs[:] al final
            dirs[:] = valid_dirs
            # Registrar directorios excluidos si se desea
            # if excluded_dirs:
            #    logger.debug("Directorios excluidos en %s: %s", current_path, excluded_dirs)
            # --- Fin Optimización ---


            # Rendimos los archivos del directorio actual que no están excluidos
            valid_files = []
            for f in files:
                file_path = current_path / f
                if not self.is_excluded(file_path):
                    valid_files.append(f)
                else:
                    # El log de exclusión ya se hace dentro de is_excluded o aquí si es necesario
                    # logger.debug("Excluyendo archivo: %s", file_path)
                    pass

            yield current_path, valid_dirs, valid_files # Yield los directorios válidos

    def analyze_repository(self) -> Dict[str, Any]:
        logger.info("Iniciando análisis en: %s", self.start_path)
        repo_analysis: Dict[str, Any] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            # Iteramos sobre los directorios y archivos válidos
            for root_path, _, valid_files in self._walk_directory():
                for file_name in valid_files:
                    file_path = root_path / file_name
                    futures[executor.submit(self.process_file, file_path)] = file_path

            logger.info("Enviados %d archivos para procesamiento.", len(futures))

            processed_count = 0
            for future in as_completed(futures):
                file_path = futures[future]
                relative_path_str = str(file_path.relative_to(self.start_path)).replace('\\', '/')
                try:
                    result = future.result()
                    if result: # Si no es None (omitido por tamaño, etc.)
                        repo_analysis[relative_path_str] = result
                except Exception as e:
                    logger.error("Error procesando futuro para %s: %s", file_path, e, exc_info=True)
                    repo_analysis[relative_path_str] = {'error': f'Processing error: {e}'}
                processed_count += 1
                if processed_count % 100 == 0:
                     logger.info("Procesados %d/%d archivos...", processed_count, len(futures))

        logger.info("Análisis de archivos completado. Se procesaron %d archivos.", len(repo_analysis))
        return repo_analysis

    def process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Procesa un archivo individual."""
        logger.debug("Procesando: %s", file_path)
        try:
            stat = file_path.stat()
            file_size = stat.st_size
        except OSError as e:
            logger.error("No se pudo obtener stat para %s: %s", file_path, e)
            return {'error': f"OS Error getting stats: {e}"}

        if file_size > self.max_file_size:
            logger.warning("Archivo %s (%d bytes) excede el límite de %d bytes. Omitiendo.",
                           file_path, file_size, self.max_file_size)
            return None # Omitir archivo

        file_info: Dict[str, Any] = {
            'path': str(file_path), # Guardar path absoluto
            'size': file_size,
            'hash': calculate_file_hash(file_path)
        }

        parser = get_parser(file_path) # Obtener el parser adecuado 
        if parser:
            try:
                parsed_data = parser.parse(file_path, file_info)
                file_info.update(parsed_data)
            except Exception as e:
                logger.error("Error durante el parsing de %s con %s: %s",
                               file_path, parser.__class__.__name__, e, exc_info=True)
                file_info['error'] = f"Parsing error ({parser.__class__.__name__}): {e}"
        else:
             logger.debug("No se encontró parser específico para: %s. Aplicando análisis genérico.", file_path)

        return file_info