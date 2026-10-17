"""
Script de Teste do Carregamento (Load) e Prova de Idempotência
1. Liga ao PostgreSQL
2. Cria tabela se não existir
3. Extrai e transforma dados
4. Carrega para o PostgreSQL (1ª vez)
5. Carrega novamente (2ª vez) e prova que a contagem de linhas NÃO duplica!
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from sqlalchemy import text
from src.database import get_engine
from src.extract import fetch_weather_type, fetch_city_forecast
from src.transform import transform_forecast_data
from src.load import init_database, load_forecasts_idempotent

def main():
    print("=== Teste de Carregamento e Idempotência no PostgreSQL ===\n")
    
    # 1. Obter engine de conexão
    engine = get_engine()
    
    # Testar conexão
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        print("[DB] Ligação ao PostgreSQL bem-sucedida!")
    except Exception as e:
        print(f"\n[ERRO DE LIGAÇÃO] Não foi possível ligar ao PostgreSQL: {e}")
        print("\nVerifica se:")
        print(" 1. O Docker Desktop está aberto e a correr.")
        print(" 2. Executaste 'docker compose up -d' no terminal.")
        return

    # 2. Inicializar tabelas e índices
    init_database(engine)

    # 3. Extrair e transformar dados de Lisboa e Porto
    print("\n[ETL] A extrair e transformar dados...")
    weather_types = fetch_weather_type()
    cidades = [{"id": 1110600, "nome": "Lisboa"}, {"id": 1131200, "nome": "Porto"}]
    
    dfs = []
    for c in cidades:
        raw = fetch_city_forecast(c["id"])
        dfs.append(transform_forecast_data(raw, c["nome"], weather_types))
    df_completo = pd.concat(dfs, ignore_index=True)
    print(f"[ETL] Total de linhas preparadas: {len(df_completo)}")

    # 4. Primeira Execução do Load
    print("\n--- 1ª Carga na Base de Dados ---")
    load_forecasts_idempotent(df_completo, engine)
    
    with engine.connect() as conn:
        count_1 = conn.execute(text("SELECT COUNT(*) FROM weather_forecasts;")).scalar()
    print(f"[VERIFICAÇÃO] Total de linhas na tabela após a 1ª carga: {count_1}")

    # 5. Segunda Execução do Load (com exatamente os mesmos dados)
    print("\n--- 2ª Carga na Base de Dados (Teste de Idempotência) ---")
    load_forecasts_idempotent(df_completo, engine)
    
    with engine.connect() as conn:
        count_2 = conn.execute(text("SELECT COUNT(*) FROM weather_forecasts;")).scalar()
    print(f"[VERIFICAÇÃO] Total de linhas na tabela após a 2ª carga: {count_2}")

    # 6. Prova de Idempotência
    if count_1 == count_2:
        print("\n PROVA DE IDEMPOTÊNCIA BEM-SUCEDIDA!")
        print(f"A base de dados manteve as {count_1} linhas sem duplicações.")
    else:
        print(f"\n❌ FALHA DE IDEMPOTÊNCIA: Havia {count_1} linhas e agora há {count_2} linhas.")

    # 7. Amostra dos dados guardados no Postgres
    print("\n--- Amostra das primeiras 3 linhas no PostgreSQL ---")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT city_name, forecast_date, t_min, t_max, precip_prob, weather_desc 
            FROM weather_forecasts 
            ORDER BY city_name, forecast_date 
            LIMIT 3;
        """))
        for row in result.mappings():
            print(dict(row))

if __name__ == "__main__":
    main()
