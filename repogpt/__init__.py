# repogpt/__init__.py

# Versión del paquete
__version__ = "0.2.0" # Actualizar según sea necesario

# Opcional: importar elementos clave para acceso directo
# from .analyzer import RepositoryAnalyzer
# from .exceptions import RepoGPTException

# Configurar un logger NullHandler por defecto para evitar mensajes si la app
# que usa la librería no configura logging.
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())