"""
Módulo de Carregamento
Responsável por criar as tabelas e persistir dados de fomra idempotente no PostgreSQL.
"""

import pandas as pd
from sqlalchemy import text

# =========================================================================================================================
# 1. Criação da Tabela e Indices
# - NUMERIC(4,1): Guarda números com 1 casa decimal exata (evita erros de aproximação de floats)
# - PRIMARY KEY (forecast_date, global_id_local): Chave composta que impede duplicados para a mesma cidade e data
# - idx_forecast_date: Índice para acelerar filtros de datas no Dashboard
# =========================================================================================================================

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_forecasts (
    global_id_local INTEGER NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    forecast_date DATE NOT NULL,
    t_min NUMERIC(4,1) NOT NULL,
    t_max NUMERIC(4,1) NOT NULL,
    precip_prob NUMERIC (5,2) NOT NULL,
    weather_type_id INTEGER NOT NULL,
    weather_desc VARCHAR(150) NOT NULL,
    wind_dir VARCHAR(10),
    wind_speed_class INTEGER,
    latitude NUMERIC(8,4),
    longitude NUMERIC(8,4),
    extracted_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (global_id_local, forecast_date)
);

CREATE INDEX IF NOT EXISTS idx_forecast_date ON weather_forecasts (forecast_date);
"""

def init_database(engine):
    """
    Cria a tabela e os indices caso não existam ainda.
    O bloco 'with engine.begin()' abre a ligação, inicia a transação e faz comit/rollback/close
    automaticamente.
    """
    with engine.begin() as connections:
        connections.execute(text(CREATE_TABLE_SQL))
    print("[LOAD] Tabela 'weather_foreacasts' iniciado com sucesso.")

def load_forecasts_idempotent(df, engine):
    """
    Insere dados na tabela de forma idempotente.
    Se (golbal_id_local, forcast_date) já existir, atualiza os valores.
    """
    if df.empty:
        print("[LOAD] Dataframe está vazio. Nenhum registo a processar.")
        return 0
    
    # =============================================================================
    # Query UPSERT:
    # - Os dois pontos (:t_min) indicam parâmetros seguros, evita SQL Injection.
    # - ON CONFLICT: deteta se a chave primária (cidade + data) já existe.
    # - EXCLUDED: representa o valor que se queria inserir, subtitui a antiga.
    # =============================================================================

    upsert_sql = """
    INSERT INTO weather_forecasts (
        global_id_local, city_name, forecast_date, t_min, t_max, precip_prob,
        weather_type_id, weather_desc, wind_dir, wind_speed_class, latitude, longitude,
        extracted_at
    ) VALUES (
        :global_id_local, :city_name, :forecast_date, :t_min, :t_max, :precip_prob,
        :weather_type_id, :weather_desc, :wind_dir, :wind_speed_class, :latitude, :longitude,
        :extracted_at
    )
    ON CONFLICT(global_id_local, forecast_date)
    DO UPDATE SET
        t_min = EXCLUDED.t_min,
        t_max = EXCLUDED.t_max,
        precip_prob = EXCLUDED.precip_prob,
        weather_type_id = EXCLUDED.weather_type_id,
        weather_desc = EXCLUDED.weather_desc,
        wind_dir = EXCLUDED.wind_dir,
        wind_speed_class = EXCLUDED.wind_speed_class,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        extracted_at = EXCLUDED.extracted_at
    """

    # Coverter o Datafram numa lista d dicinários para execução em lote
    registos = df.to_dict(orient="records")
    
    # Garante que as datas do Pandas são enviadas no formato DATE nativo para o PostgreSQL
    for r in registos:
        if isinstance(r["forecast_date"], pd.Timestamp):
            r["forecast_date"] = r["forecast_date"].date()
    
    # Executa a inserção de todas as linhas de uma só vez dentro de uma transação segura
    with engine.begin() as connection:
        connection.execute(text(upsert_sql), registos)
    
    print(f"[LOAD] {len(registos)} registos processados idempotentes.")
    return len(registos)
