# repogpt/utils/file_utils.py

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CHUNK_SIZE = 8192  # Leer archivos en bloques de 8KB para hashing


def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str | None:
    """
    Calcula el hash de un archivo usando el algoritmo especificado.

    Args:
        file_path: Ruta al archivo.
        algorithm: Algoritmo de hash a usar (ej. 'sha256', 'md5').

    Returns:
        El hash en formato hexadecimal como string, o None si ocurre un error.
    """
    try:
        hasher = hashlib.new(algorithm)
        with file_path.open("rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        logger.error("Archivo no encontrado al calcular hash: %s", file_path)
    except PermissionError:
        logger.error("Permiso denegado al calcular hash para: %s", file_path)
    except OSError as e:
        logger.error("Error de OS calculando hash para %s: %s", file_path, e)
    except ValueError:
        logger.error("Algoritmo de hash inválido: %s", algorithm)
    except Exception as e:
        logger.error(
            "Error inesperado calculando hash para %s: %s", file_path, e, exc_info=True
        )

    return None


def is_likely_binary(file_path: Path, check_bytes: int = 1024) -> bool:
    """
    Intenta determinar si un archivo es probablemente binario.

    Actualmente usa una heurística simple: la presencia de un byte NULL
    dentro de los primeros 'check_bytes'.

    Args:
        file_path: Ruta al archivo.
        check_bytes: Número de bytes iniciales a revisar.

    Returns:
        True si el archivo parece binario, False en caso contrario o si hay error.
    """
    try:
        with file_path.open("rb") as f:
            chunk = f.read(check_bytes)
            if b"\x00" in chunk:
                logger.debug(
                    "Detectado byte NULL en %s, marcando como binario.", file_path
                )
                return True
            # Podríamos añadir más heurísticas aquí si fuera necesario
            # Por ejemplo, buscar un alto porcentaje de caracteres no imprimibles.
    except FileNotFoundError:
        logger.warning(
            "Archivo no encontrado al verificar si es binario: %s", file_path
        )
        return False  # No se puede determinar, asumir no binario por seguridad
    except PermissionError:
        logger.warning("Permiso denegado al verificar si es binario: %s", file_path)
        return False  # Asumir no binario
    except OSError as e:
        logger.warning("Error de OS verificando si %s es binario: %s", file_path, e)
        return False  # Asumir no binario
    except Exception as e:
        logger.warning(
            "Error inesperado verificando si %s es binario: %s", file_path, e
        )
        return False  # Asumir no binario

    logger.debug("%s no parece binario (basado en byte NULL).", file_path)
    return False


# Podrías añadir aquí otras utilidades relacionadas con archivos si las necesitas.
