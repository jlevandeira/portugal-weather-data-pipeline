"""
Módulo de Logging Centralizado
Configura saída dupla: consola (terminal) e ficheiro de texto rotativo (logs/pipeline.log).
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Cria a pasta logs/ na raiz do projeto se ainda não existir
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "pipeline.log"

def setup_logger(name: str = "pipeline", level: str = None) -> logging.Logger:
    """Configura e retorna um logger padronizado para o projeto."""
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evita adicionar múltiplos handlers se a função for chamada mais de uma vez
    if logger.handlers:
        return logger

    # Formato do log: [Data Hora] [Nível] [Módulo]: Mensagem
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Handler para a Consola (Terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Handler para Ficheiro Rotativo (Máx 2MB por ficheiro, guarda até 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
