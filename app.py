"""
Dashboard Meteorológico de Portugal
Interface interativa em Streamlit alimetada pelo Postgresql
"""

import streamlit as st
import pandas as pd 
from sqlalchemy import text
from src.database import get_engine

# 1. Configuração da Pagina
st.set_page_config(
    page_title = "Metereologia de Portugal",
    page_icon = "",
    layout = "wide"
)

# 2. Função de leitura com Cache (ideal para Performance)
@st.cache_data(ttl=60)
def load_data():
    engine = get_engine()
    query = """
        SELECT
            city_name,
            forecast_date,
            t_min,
            t_max,
            precip_prob,
            weather_desc,
            wind_dir,
            wind_speed_class,
            latitude,
            longitude,
            extracted_at
        FROM weather_forecasts
        ORDER BY city_name, forecast_date ASC;
    """
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    
    # Conversão de decimal do postgresql para float
    df["t_min"] = df["t_min"].astype(float)
    df["t_max"] = df["t_max"].astype(float)
    df["precip_prob"] = df["precip_prob"].astype(float)
    df["forecast_date"] = pd.to_datetime(df["forecast_date"]).dt.date
    return df
    
# Carrega os dados
df = load_data()

# Se a base de dados ainda estiver vazia
if df.empty:
    st.warning("Nenhum dado encontrado na base de dados. Executa a pipeline primeiro!")
    st.stop()

# =========================================================
# 3. Barra Lateral (Filtros e controlos)
# =========================================================

st.sidebar.title("Filtros & Opções")

# Dropdown de cidade disponíveis
cidades_disp = sorted(df["city_name"].unique())
cidade_selec = st.sidebar.selectbox("Seleciona uma Cidade:", cidades_disp)

# Botão para limpar a cache e forçar a atualização da base de dados
if st.sidebar.button("Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Metadados de extração
ultima_extracao = df["extracted_at"].max()
st.sidebar.markdown("---")
st.sidebar.caption(f" **Última extração:** {ultima_extracao.strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.sidebar.caption(" **Fonte:** API Open Source IPMA")

# Filtra o Dataframe para a cidade selecionada
df_cidade = df[df["city_name"] == cidade_selec].sort_values("forecast_date")

dias_pt = {
    0: "Seg",
    1: "Ter",
    2: "Qua",
    3: "Qui",
    4: "Sex",
    5: "Sab",
    6: "Dom",
}

df_cidade["data_formatada"] = df_cidade["forecast_date"].apply(
    lambda d: f"{dias_pt[pd.to_datetime(d).weekday()]}, {pd.to_datetime(d).strftime('%d/%m')}"
)

# =========================================================
# 4. Cabeçalho e cartões de Métricas (KPIs)
# =========================================================
st.title(f"Previsão Meteorológica - {cidade_selec}")
st.markdown("Previsão oficial do IPMA a 5 dias persistida no PostgreSQL.")

# Cartões de Métricas no topo
col1, col2, col3, col4 = st.columns(4)

hoje = df_cidade.iloc[0]
temp_maxima_periodo = df_cidade["t_max"]. max()
temp_minima_periodo = df_cidade["t_min"].min()
prob_chuva_maxima = df_cidade["precip_prob"].max()

with col1:
    st.metric(label= "Temperatura Máxima (5 dias)", value=f"{temp_maxima_periodo} °C")
with col2:
    st.metric(label= "Temperatura Mínima (5 dias)", value=f"{temp_minima_periodo} °C")
with col3:
    st.metric(label="Probabilidade de Chuva", value=f"{(prob_chuva_maxima/100)}")
with col4:
    st.metric(label="Estado Hoje", value=hoje["weather_desc"])

# =========================================================
# 5. Visualizações Gráficas
# =========================================================
st.subheader("Evolução das Temperaturas a 5 dias")

# Gráficos de linhas: Temp mins e max
df_grafico_temp = df_cidade.set_index("data_formatada")[["t_min", "t_max"]]
df_grafico_temp.columns = ["Temp. Minima (ºC)", "Temp. Máxima (ºC)"]
st.line_chart(df_grafico_temp, use_container_width = True)

st.subheader("Probabilidade de Percipitação (%)")

# Gráfico de barras: Chuva
df_grafico_chuva = df_cidade.set_index("data_formatada")[["precip_prob"]]
df_grafico_chuva.columns = ["Probabilidade de Chuva (%)"]
st.bar_chart(df_grafico_chuva, use_container_width=True)

st.markdown("---")

# =========================================================
# 6. Tabela detalhada e exportação d dados
# =========================================================
st.subheader("Tabela completa de Previsões")

colunas_apresent = {
    "forecast_date": "Data",
    "t_min": "T. Min (ºC)",
    "t_max": "T. Max (ºC)",
    "precip_prob": "Chuva (%)",
    "wind_dir": "Vento",
    "wind_speed_class": "Classe Vento",
}

tabela_final = df_cidade[list(colunas_apresent.keys())].rename(columns=colunas_apresent)
st.dataframe(tabela_final, hide_index=True, use_container_width=True)

# Download em CSV
csv = tabela_final.to_csv(index=False).encode("utf-8")
st.download_button(
    label = "Decarregar dados em CSV",
    data=csv,
    file_name=f"previsao_{cidade_selec.lower()}.csv",
    mime ="text/csv"
)