# repogpt/extractors/dependencies.py

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import ExtractorModule
from repogpt.analyzer import RepositoryAnalyzer # Importación directa ahora es segura

try:
    import yaml
except ImportError:
    yaml = None
    logging.debug("PyYAML no instalado, no se analizarán archivos .yaml para dependencias.")

try:
    import toml
except ImportError:
    toml = None
    logging.debug("toml library no instalado, no se analizarán archivos pyproject.toml.")


logger = logging.getLogger(__name__)

class DependencyExtractor(ExtractorModule):
    """Extrae información de dependencias de archivos comunes."""

    # Mapeo de nombres de archivo a métodos de parseo
    dependency_parsers = {
        'package.json': '_parse_package_json',
        'requirements.txt': '_parse_requirements_txt',
        'Pipfile': '_parse_pipfile',
        'pyproject.toml': '_parse_pyproject',
        # 'poetry.lock': '_parse_poetry_lock', # Lock files can be very large, maybe skip?
        'environment.yaml': '_parse_environment_yaml', # Common for Conda
        'environment.yml': '_parse_environment_yaml',
        # Añadir más si es necesario: Gemfile, go.mod, pom.xml, build.gradle, etc.
    }

    def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Busca y parsea archivos de dependencias conocidos en la raíz del repo."""
        logger.info("Buscando archivos de dependencias...")
        deps: Dict[str, Any] = {}
        repo_root = analyzer.repo_path # Usar el path base del analyzer

        for file_name, parser_method_name in self.dependency_parsers.items():
            file_path = repo_root / file_name
            if file_path.exists():
                logger.debug("Encontrado archivo de dependencias: %s", file_path)
                parser_method = getattr(self, parser_method_name, None)
                if parser_method:
                    try:
                        deps[file_name] = parser_method(file_path)
                        logger.info("Dependencias extraídas de: %s", file_name)
                    except Exception as e:
                        logger.error("Error procesando archivo de dependencias %s: %s", file_name, e, exc_info=True)
                        deps[file_name] = {'_error': f'Failed to parse: {e}'}
                else:
                     logger.warning("Método parser '%s' no encontrado en DependencyExtractor.", parser_method_name)
            else:
                logger.debug("Archivo de dependencias no encontrado: %s", file_path)

        return {"dependencies": deps} # Devuelve bajo la clave 'dependencies'

    # --- Métodos de Parseo Específicos ---

    def _parse_package_json(self, path: Path) -> Dict[str, Any]:
        logger.debug("Parseando %s", path.name)
        try:
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
            # Extraer solo las secciones relevantes
            return {
                'name': data.get('name'),
                'version': data.get('version'),
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {}),
                'peerDependencies': data.get('peerDependencies', {}),
                'optionalDependencies': data.get('optionalDependencies', {}),
            }
        except json.JSONDecodeError as e:
            logger.error("Error de JSON en %s: %s", path.name, e)
            return {'_error': f'Invalid JSON: {e}'}

    def _parse_requirements_txt(self, path: Path) -> List[str]:
        logger.debug("Parseando %s", path.name)
        lines: List[str] = []
        try:
            with path.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Omitir comentarios y líneas vacías, manejar continuaciones básicas
                    line = re.sub(r'\s+#.*$', '', line) # Quitar comentarios en línea
                    if line and not line.startswith('#'):
                        # Simple manejo de continuación de línea (puede no ser perfecto)
                        while line.endswith('\\'):
                            line = line[:-1].strip() + next(f, '').strip()
                        lines.append(line)
            return lines
        except Exception as e:
            logger.error("Error leyendo %s: %s", path.name, e)
            return [{'_error': f'Error reading file: {e}'}] # Devuelve error como parte de la lista? O solo log?

    def _parse_pipfile(self, path: Path) -> Dict[str, Any]:
        logger.debug("Parseando %s", path.name)
        if toml is None:
            return {'_error': 'toml library not installed'}
        try:
            data = toml.load(path)
            return {
                'packages': data.get('packages', {}),
                'dev-packages': data.get('dev-packages', {})
            }
        except toml.TomlDecodeError as e:
            logger.error("Error de TOML en %s: %s", path.name, e)
            return {'_error': f'Invalid TOML: {e}'}

    def _parse_pyproject(self, path: Path) -> Dict[str, Any]:
        logger.debug("Parseando %s", path.name)
        if toml is None:
            return {'_error': 'toml library not installed'}
        try:
            data = toml.load(path)
            # Buscar dependencias en varias secciones comunes (Poetry, PDM, build-system)
            dependencies = {}
            if poetry_deps := data.get('tool', {}).get('poetry', {}).get('dependencies'):
                dependencies['poetry'] = poetry_deps
            if pdm_deps := data.get('project', {}).get('dependencies'):
                 dependencies['pdm/build'] = pdm_deps # PEP 621
            if build_reqs := data.get('build-system', {}).get('requires'):
                 dependencies['build-system'] = build_reqs
            return dependencies
        except toml.TomlDecodeError as e:
            logger.error("Error de TOML en %s: %s", path.name, e)
            return {'_error': f'Invalid TOML: {e}'}

    def _parse_environment_yaml(self, path: Path) -> Dict[str, Any]:
        logger.debug("Parseando %s", path.name)
        if yaml is None:
            return {'_error': 'PyYAML library not installed'}
        try:
            with path.open('r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return {
                'name': data.get('name'),
                'channels': data.get('channels', []),
                'dependencies': data.get('dependencies', [])
            }
        except yaml.YAMLError as e:
            logger.error("Error de YAML en %s: %s", path.name, e)
            return {'_error': f'Invalid YAML: {e}'}