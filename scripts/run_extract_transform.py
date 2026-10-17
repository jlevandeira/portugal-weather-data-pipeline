"""
Script de Teste do Fluxo Extract + Transform
Executa a extração para Lisboa e Porto, passa pelo Transform e exibe o DataFrame resultante.
"""

import sys
from pathlib import Path

# Garante que a raiz do projeto está no PYTHONPATH para importar o pacote 'src'
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.extract import fetch_weather_type, fetch_city_forecast
from src.transform import transform_forecast_data
import pandas as pd

def main():
    print("=== Teste do Fluxo: Extract & Transform ===")
    
    # 1. Obter mapa de tipos de tempo (dimensão)
    print("\n[1/3] A carregar dicionário de tipos de tempo...")
    weather_types = fetch_weather_type()
    print(f"Total de tipos carregados: {len(weather_types)} (Ex: Tipo 1 = '{weather_types.get(1)}')")
    
    # 2. Extrair dados para Lisboa (1110600) e Porto (1131200)
    cidades = [
        {"id": 1110600, "nome": "Lisboa"},
        {"id": 1131200, "nome": "Porto"},
    ]
    
    dfs = []
    for c in cidades:
        print(f"\n[2/3] A extrair previsão para {c['nome']} (ID: {c['id']})...")
        raw = fetch_city_forecast(c["id"])
        
        print(f"[3/3] A transformar dados de {c['nome']}...")
        df_cidade = transform_forecast_data(raw, c["nome"], weather_types)
        dfs.append(df_cidade)
        
    # Combina os DataFrames das cidades num só
    df_final = pd.concat(dfs, ignore_index=True)
    
    print("\n=== Resultado da Transformação ===")
    print(f"Dimensões do DataFrame final: {df_final.shape[0]} linhas x {df_final.shape[1]} colunas\n")
    
    print("Tipos de dados das colunas (dtypes):")
    print(df_final.dtypes)
    
    print("\nPrimeiras 4 linhas do DataFrame:")
    colunas_visiveis = ["city_name", "forecast_date", "t_min", "t_max", "precip_prob", "weather_desc"]
    colunas_presentes = [col for col in colunas_visiveis if col in df_final.columns]
    print(df_final[colunas_presentes].head(4).to_string())

if __name__ == "__main__":
    main()
