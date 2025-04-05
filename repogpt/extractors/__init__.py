# repogpt/extractors/__init__.py

# Importar los módulos específicos para que se registren o sean accesibles
from . import dependencies
from . import git
from . import metrics
from . import structure
from . import todos

# Re-exportar la clase base para conveniencia
from .base import ExtractorModule

__all__ = [
    'ExtractorModule',
    'dependencies',
    'git',
    'metrics',
    'structure',
    'todos',
]