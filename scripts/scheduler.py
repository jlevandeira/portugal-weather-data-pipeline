"""
Scheduler
Executa a pipeline periodicamente em background a cada X minutos ou horas.
"""

import sys
import time
import os
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.pipeline import run_pipeline
from src.logger import setup_logger

logger = setup_logger("scheduler")

# Intervalo entre excuções em segundos

INTERVAL_SECONDS = int(os.getenv("SCHEDULE_INTERVAL_SECONDS", "60"))

def main():
    logger.info(f"=== Scheduler iniciado! Intervalo configurado: {INTERVAL_SECONDS} segundos ===")
    logger.info(" CTRL+C no terminal para parar o scheduler a qualque momento.\n")

    ciclo = 1
    try:
        while True:
            logger.info(f"--- [Ciclo #{ciclo}] Início da execução: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
            resultado = run_pipeline() # Executa toda a pipeline

            logger.info(f"--- [Ciclo #{ciclo}] Fim da execução. Próximo ciclo em {INTERVAL_SECONDS}s ---\n ")
            ciclo +=1

            # Aguarda até o próximo intervalo
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.warning("\n [SHUTDOWN] Scheduler interrompido manualmente pelo user. A encerrar com segurança.")

if __name__ == "__main__":
    main()