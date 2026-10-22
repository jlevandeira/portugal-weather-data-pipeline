"""
Testes Unitários para o Módulo de Transformação (src/transform.py)
Utiliza pytest e dados simulados (fixtures) sem necessidade de ligação à internet.
"""

import pytest
import pandas as pd
from src.transform import transform_forecast_data

# =============================================================================
# Fixtures: Cenários de Dados Fictícios para Testes
# =============================================================================
@pytest.fixture
def mock_weather_types():
    """Dicionário simulado de tipos de tempo."""
    return {
        1: "Céu limpo",
        2: "Céu pouco nublado",
        9: "Chuva/aguaceiros"
    }

@pytest.fixture
def mock_raw_forecast():
    """Exemplo de resposta JSON bruta da API do IPMA com strings nos números."""
    return {
        "globalIdLocal": 1110600,
        "dataUpdate": "2026-10-22T10:00:00",
        "data": [
            {
                "precipitaProb": "10.0",
                "tMin": "14.5",
                "tMax": "22.0",
                "predWindDir": "NW",
                "idWeatherType": 1,
                "classWindSpeed": 1,
                "longitude": "-9.1286",
                "forecastDate": "2026-10-22",
                "latitude": "38.7660"
            },
            {
                "precipitaProb": "80.5",
                "tMin": "16.0",
                "tMax": "19.5",
                "predWindDir": "W",
                "idWeatherType": 9,
                "classWindSpeed": 2,
                "longitude": "-9.1286",
                "forecastDate": "2026-10-23",
                "latitude": "38.7660"
            }
        ]
    }

# =============================================================================
# Casos de Teste (Test Cases)
# =============================================================================

def test_transform_types_conversion(mock_raw_forecast, mock_weather_types):
    """Verifica se as strings numéricas foram convertidas para float e int."""
    df = transform_forecast_data(mock_raw_forecast, "Lisboa", mock_weather_types)
    
    # 1. Deve conter exatamente 2 linhas
    assert len(df) == 2
    
    # 2. As temperaturas têm de ser float, não string
    assert df["t_min"].dtype == "float64"
    assert df["t_max"].dtype == "float64"
    assert df["precip_prob"].dtype == "float64"
    
    # 3. Valores exatos convertidos
    assert df.iloc[0]["t_min"] == 14.5
    assert df.iloc[0]["t_max"] == 22.0
    assert df.iloc[0]["precip_prob"] == 10.0

def test_transform_weather_desc_enrichment(mock_raw_forecast, mock_weather_types):
    """Verifica se o idWeatherType foi corretamente traduzido para texto."""
    df = transform_forecast_data(mock_raw_forecast, "Lisboa", mock_weather_types)
    
    # O dia 1 tem idWeatherType=1 -> "Céu limpo"
    assert df.iloc[0]["weather_desc"] == "Céu limpo"
    
    # O dia 2 tem idWeatherType=9 -> "Chuva/aguaceiros"
    assert df.iloc[1]["weather_desc"] == "Chuva/aguaceiros"

def test_transform_metadata_columns(mock_raw_forecast, mock_weather_types):
    """Verifica se as colunas de auditoria e contexto de cidade foram adicionadas."""
    df = transform_forecast_data(mock_raw_forecast, "Lisboa", mock_weather_types)
    
    assert "city_name" in df.columns
    assert df.iloc[0]["city_name"] == "Lisboa"
    assert df.iloc[0]["global_id_local"] == 1110600
    assert "extracted_at" in df.columns

def test_transform_empty_data(mock_weather_types):
    """Testa caso limite (edge case): se a API devolver uma lista vazia."""
    empty_payload = {"globalIdLocal": 1110600, "data": []}
    df = transform_forecast_data(empty_payload, "Lisboa", mock_weather_types)
    
    # Deve retornar um DataFrame vazio sem rebentar com erro
    assert df.empty