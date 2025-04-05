# repogpt/extractors/git.py
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict

from .base import ExtractorModule
from repogpt.analyzer import RepositoryAnalyzer

logger = logging.getLogger(__name__)

class GitInfoExtractor(ExtractorModule):
    """Extrae información del repositorio Git si existe."""

    def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta comandos git para obtener información del último commit, rama, etc."""
        repo_path = analyzer.repo_path
        git_dir = repo_path / ".git"

        if not git_dir.exists():
            logger.info("Directorio .git no encontrado en %s. Omitiendo extracción Git.", repo_path)
            return {}

        logger.info("Extrayendo información de Git desde: %s", repo_path)
        git_info: Dict[str, Any] = {}
        repo_str = str(repo_path) # Para usar con -C

        # Comandos a ejecutar y la clave bajo la cual guardar el resultado
        commands = {
            'commit_hash': ['rev-parse', 'HEAD'],
            'commit_short_hash': ['rev-parse', '--short', 'HEAD'],
            'commit_message': ['log', '-1', '--pretty=%B'],
            'author_name': ['log', '-1', '--pretty=%an'],
            'author_email': ['log', '-1', '--pretty=%ae'],
            'commit_date': ['log', '-1', '--pretty=%cI'], # ISO 8601
            'branch': ['rev-parse', '--abbrev-ref', 'HEAD'],
            'tags': ['tag', '--points-at', 'HEAD'],
            'remotes': ['remote', '-v'],
            # 'last_commit_stats': ['show', '--stat', '--oneline', 'HEAD'] # Puede ser muy largo
        }

        for key, cmd in commands.items():
            try:
                # Usar stderr=subprocess.PIPE para capturar errores de git
                process = subprocess.run(
                    ['git', '-C', repo_str] + cmd,
                    capture_output=True,
                    text=True, # Decodificar salida como texto
                    check=False, # No lanzar excepción si git falla, lo manejamos abajo
                    encoding='utf-8', # Especificar encoding
                    errors='replace'  # Manejar errores de decodificación
                )
                if process.returncode == 0:
                    output = process.stdout.strip()
                    # Procesar salida específica si es necesario
                    if key == 'remotes':
                        remotes_list = []
                        for line in output.splitlines():
                             parts = line.split()
                             if len(parts) >= 2:
                                 remotes_list.append({'name': parts[0], 'url': parts[1]})
                        git_info[key] = remotes_list
                    elif key == 'tags':
                         git_info[key] = output.splitlines()
                    else:
                         git_info[key] = output
                    logger.debug("Git %s: %s", key, git_info[key])
                else:
                    error_msg = process.stderr.strip()
                    logger.warning("Comando git falló para '%s': %s (código: %d)",
                                   key, error_msg or "Sin salida de error", process.returncode)
                    git_info[key] = f"_error: Git command failed (code {process.returncode})"

            except FileNotFoundError:
                 logger.error("Comando 'git' no encontrado. Asegúrate de que Git esté instalado y en el PATH.")
                 git_info['_error_git_not_found'] = "Git command not found."
                 break # No intentar más comandos si git no existe
            except Exception as e:
                logger.error("Error inesperado ejecutando comando git para '%s': %s", key, e, exc_info=True)
                git_info[key] = f"_error: Unexpected error ({e})"

        return {"git_info": git_info}