"""
Módulo de extração de dados
Responsável exclusivamente por comunicar com a API do IPMA e retornar os dados brutos
"""

import requests

BASE_URL = "https://api.ipma.pt/open-data"
TIMEOUT_SEG = 10

def fetch_districts_and_islands():
    """Obtém a lista de todas as localidades disponiveis no IPMA"""
    endpoint = f"{BASE_URL}/distrits-islands.json"
    try:
        response = requests.get(endpoint, timeout=TIMEOUT_SEG)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"[EXTRACT ERROR] Falha ao obter lista de distritos: {e}")
        raise

def fetch_weather_type():
    """Obtém o glossário de tipos de tempo, {1: 'Céu limpo', 2: 'Céu pouco nublado'}"""
    endpoint = f"{BASE_URL}/weather-type-classe.json"
    try:
        response = requests.get(endpoint, timeout=TIMEOUT_SEG)
        response.raise_for_status()
        data = response.json().get("data", [])
        
        weather_types = {}
        for item in data:
            codigo = item["idWeatherType"]
            desc = item["descWeatherTypePT"]
            weather_types[codigo] = desc
        return weather_types
    except requests.exceptions.RequestException as e:
        print(f"[EXTRACT ERROR] Falha ao obter tipos de tempo: {e}")
        raise

def fetch_city_forecast(global_id_local):
    """Obtém a previsão diária de uma cidade"""
    endpoint = f"{BASE_URL}/forecast/meteorology/cities/daily/{global_id_local}.json"
    try:
        response = requests.get(endpoint, timeout=TIMEOUT_SEG)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[EXTRACT ERROR] Falha ao obter previsão para local {global_id_local}: {e}")
        raise