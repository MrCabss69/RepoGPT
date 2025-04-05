# repogpt/utils/logging.py
import logging
import sys

def configure_logging(log_level: str) -> None:
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    level = levels.get(log_level.upper())
    if level is None:
        raise ValueError(f"Nivel de log inválido: {log_level}. Usar: {', '.join(levels.keys())}")

    # Configuración básica (podría ser más avanzada)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("repogpt_analyzer.log"), # Renombrado
            logging.StreamHandler(sys.stdout) # Usar stdout
        ]
    )
    # Silenciar logs muy verbosos de otras librerías si es necesario
    # logging.getLogger("some_library").setLevel(logging.WARNING)