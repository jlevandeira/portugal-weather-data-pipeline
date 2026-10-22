"""
Módulo da Pipeline (ETL)
Responsável por coordenar o fluxo Extract - Transform - Load para todas as cidades.
"""
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para reconhecer a pasta 'src'
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import os
from dotenv import load_dotenv
from src.logger import setup_logger
from src.database import get_engine
from src.extract import fetch_weather_type, fetch_city_forecast, fetch_districts_and_islands
from src.transform import transform_forecast_data
from src.load import init_database, load_forecasts_idempotent

# Carrega variáveis de ambient e inicia o logger
load_dotenv()
logger = setup_logger("etl_pipeline")

DEFAULT_CITIES = {
    1110600: "Lisboa",
    1131200: "Porto",
    1080500: "Faro",
    1060300: "Coimbra",
}

def run_pipeline():
    """
    Executa um ciclo completo de ETL com tolerÂncia a falhas.
    Retorna um resumo com o número de cidade e registos porcessados.
    """

    logger.info("=== A iniciar o ciclo da Pipeline ===")

    # 1. Obter ligação à base de dados e garantir que a tabela existe
    try:
        engine = get_engine()
        init_database(engine)
    except Exception as e:
        logger.critical(f"Falha fatal ao conectar à base de dados: {e}")
        raise e
    
    # 2. Obter mapa de tipos de tempo
    try:
        weather_types = fetch_weather_type()
        logger.info(f"Dicionário de tipos de tempo carregado ({len(weather_types)} categories).")
    except Exception as e:
        logger.critical(f"Falha fatal ao obter tipos de tempo do IPMA: {e}")
        raise e
    
    # 3. Obter lista de distritos e ilhas
    try:
        locais = fetch_districts_and_islands()
        # Coverte a lista idlocal em Nome da cidade
        cidades = {}

        for item in locais:
            id_local = item["globalIdLocal"]
            nome_cidade = item["local"]

            cidades[id_local] = nome_cidade
        
        logger.info(f"Lista do IPMA obtida com sucesso: {len(cidades)} localidades.")
    except Exception as e:
        logger.warning(f"Faljas ao obter lista do IPMA ({e}). A usar cidades padrão.")
        cidades = DEFAULT_CITIES
    
    # 4. Processar cada cidade com isolamento de falhas
    sucesso = 0
    erros = 0
    registos = 0

    for city_id, city_name in cidades.items():
        logger.info(f"A processar cidade: {city_name} (ID: {city_id})")

        try:
            # EXTRACT: Obter JSON bruto da previsão
            raw_data = fetch_city_forecast(city_id)

            # TRANSFORM: Limpar e estruturar dados
            df_clean = transform_forecast_data(raw_data, city_name, weather_types)

            # LOAD: Persistir de forma idempotente no PostgreSQL
            rows_loaded = load_forecasts_idempotent(df_clean, engine)

            registos += rows_loaded
            sucesso += 1
            logger.info(f" {city_name} concluído com sucesso ({rows_loaded} previsões atualizadas).")
        
        except Exception as e:
            # Caso uma cidade falhe, não deita a pipeline abaixo para as outras
            erros += 1 
            logger.info(f" Falha ao processar {city_name}: {e}")
        
    resumo = {
        "cidades_sucesso": sucesso,
        "cidades_erro": erros,
        "total_registos": registos
    }
    logger.info(f"=== Ciclo concluído: {sucesso} cidades OK, {erros} erros, {registos} registos no Postgres ===")
    return resumo

if __name__ == "__main__":
    run_pipeline()
