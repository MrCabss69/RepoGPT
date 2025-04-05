# repogpt/parsers/__init__.py
import logging
from . import python
from . import markdown
from . import javascript
from . import yaml_parser
from . import html
# from . import dockerfile_
from . import generic # Importar el genérico/fallback si existe


# Re-exportar la función principal para obtener parsers
from .base import get_parser

__all__ = ['get_parser']