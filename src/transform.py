"""
Módulo de Transformação (Transform)
Responsável por limpar, tipar e enriquecer os dados brutos com Pandas.
"""

import pandas as pd
from typing import Dict, Any

def transform_forecast_data(
    raw_forecast: Dict[str, Any], 
    city_name: str, 
    weather_types_map: Dict[int, str]
) -> pd.DataFrame:
    """
    Recebe os dados brutos de previsão de uma cidade e devolve um DataFrame normalizado.
    
    Tarefas a realizar:
    1. Criar o DataFrame a partir da lista raw_forecast["data"].
    2. Adicionar as colunas de identificação da cidade (city_name e global_id_local).
    3. Converter os tipos de dados (strings para float/int/datetime).
    4. Mapear o idWeatherType para a descrição textual em português.
    5. Adicionar a coluna de auditoria 'extracted_at'.
    6. Renomear as colunas para o padrão snake_case (ex: tMin -> t_min).
    """
    data_list = raw_forecast.get("data", [])
    if not data_list:
        return pd.DataFrame()

    # 1. Criação do DataFrame
    df = pd.DataFrame(data_list)

    # 2. Adicionar colunas contextuais da cidade
    df["city_name"] = city_name
    df["global_id_local"] = raw_forecast.get("globalIdLocal")
    df['tMin'] = df['tMin'].astype(float)
    df['tMax'] = df['tMax'].astype(float)
    df['precipitaProb'] = df['precipitaProb'].astype(float)
    df['forecastDate'] = pd.to_datetime(df['forecastDate'])
    df['weather_desc'] = df['idWeatherType'].map(weather_types_map)
    df["extracted_at"] = pd.Timestamp.now(tz="UTC")
    
    # 3. Normalização dos nomes das colunas para snake_case
    colunas_renomeadas = {
        "forecastDate": "forecast_date",
        "tMin": "t_min",
        "tMax": "t_max",
        "precipitaProb": "precip_prob",
        "predWindDir": "wind_dir",
        "classWindSpeed": "wind_speed_class",
        "idWeatherType": "weather_type_id",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    df = df.rename(columns=colunas_renomeadas)
    
    # Converte latitude e longitude para float se existirem
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = df["latitude"].astype(float)
        df["longitude"] = df["longitude"].astype(float)
        
    return df