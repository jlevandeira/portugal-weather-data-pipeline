"""
Script de Exploração: API Aberta do IPMA
Objetivo: Inspecionar o formato dos dados retornados pela API e entender o schema.

Endpoints do IPMA utilizados:
1. Cidades/Locais: https://api.ipma.pt/open-data/distrits-islands.json
2. Previsão diária a 5 dias: https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/{globalIdLocal}.json
"""

import requests
import json

BASE_URL = "https://api.ipma.pt/open-data"

def explorar_locais():
    url = f"{BASE_URL}/distrits-islands.json"
    print(f"\n--- 1. A contactar endpoint de locais: {url} ---")  
    # -------------------------------------------------------------------------
    # DESAFIO 1:
    # 1. Faz o pedido GET com a biblioteca requests.
    # 2. Verifica se o pedido correu bem (dica: response.raise_for_status()).
    # 3. Converte a resposta para um dicionário Python usando .json().
    # -------------------------------------------------------------------------   
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    dados = response.json()
    
    # A lista de cidades está dentro da chave 'data'
    locais = dados.get("data", [])
    print(f"Total de locais encontrados: {len(locais)}")
    
    # Mostra os primeiros 3 locais para inspecionar os campos
    print("\nExemplo dos primeiros 3 locais:")
    for local in locais[:3]:
        print(f" - Nome: {local['local']} | ID Global: {local['globalIdLocal']} (Lat: {local['latitude']}, Lon: {local['longitude']})")
    
    return locais

def explorar_previsao(global_id_local: int):
    url = f"{BASE_URL}/forecast/meteorology/cities/daily/{global_id_local}.json"
    print(f"\n--- 2. A contactar previsão para globalIdLocal={global_id_local}: {url} ---")
    
    # -------------------------------------------------------------------------
    # DESAFIO 2:
    # Faz o mesmo para a previsão diária da cidade indicada.
    # -------------------------------------------------------------------------
    response = requests.get(url)
    response.raise_for_status()
    dados = response.json()
    
    previsoes = dados.get("data", [])
    data_atualizacao = dados.get("dataUpdate", "Desconhecida")
    print(f"Previsões disponíveis: {len(previsoes)} dias (Última atualização: {data_atualizacao})")
    
    # Inspeciona a previsão do primeiro dia
    if previsoes:
        primeiro_dia = previsoes[0]
        print("\nEstrutura do primeiro dia de previsão:")
        print(json.dumps(primeiro_dia, indent=2))

if __name__ == "__main__":
    try:
        locais = explorar_locais()
        # Lisboa tem o globalIdLocal = 1110600
        # Porto tem o globalIdLocal = 1131200
        explorar_previsao(global_id_local=1110600)
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema ao executar: {e}")
