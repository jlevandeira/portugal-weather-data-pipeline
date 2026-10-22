# 🌤️ Portugal Weather Data Pipeline & Analytics Dashboard

[![CI](https://github.com/jlevandeira/portugal-weather-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/jlevandeira/portugal-weather-data-pipeline/actions)
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit)

Pipeline de dados automatizada de ponta a ponta (*End-to-End ETL*) que recolhe, valida e persiste previsões meteorológicas oficiais para ~35 localidades de Portugal a partir da API aberta do **IPMA** (Instituto Português do Mar e da Atmosfera), disponibilizando visualizações analíticas em tempo real através de um dashboard interativo em **Streamlit**.

---

## Arquitetura da Solução

```text
[ API Aberta do IPMA ]
        │
        ▼ (HTTP GET / JSON com timeouts defensivos)
┌────────────────────────────────────────────────────────┐
│             Pipeline ETL em Python (Batch)             │
│  - Extract: recolha dinâmica de ~35 distritos e ilhas  │
│  - Transform: limpeza e tipagem estrita com Pandas     │
│  - Load: persistência relacional com SQLAlchemy        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (UPSERT Idempotente / Porta 5432)
┌────────────────────────────────────────────────────────┐
│             PostgreSQL 16 (Docker Container)           │
│  - Tabela: weather_forecasts (PK: cidade + data)       │
│  - Índices secundários B-Tree para queries rápidas     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (Queries SQL com cache @st.cache_data)
┌────────────────────────────────────────────────────────┐
│             Dashboard Streamlit (Container)            │
│  - KPIs, gráficos de temperatura e probabilidade chuva │
│  - Filtros dinâmicos e exportação de dados em CSV      │
└────────────────────────────────────────────────────────┘

Camadas Transversais:
 - Orquestração: Scheduler em background a cada X minutos (com tolerância a falhas).
 - Qualidade: Testes unitários com pytest e CI automático no GitHub Actions.
```

---

## Decisões Técnicas de Engenharia & Trade-offs

### 1. ETL vs ELT
* **Decisão:** Adotei o padrão **ETL clássico** utilizando Pandas em memória antes da inserção na base de dados.
* **Justificação:** A API aberta do IPMA serializa valores numéricos e datas como strings JSON. A conversão e validação antecipada de tipos garante integridade relacional estrita no PostgreSQL, permitindo que a base de dados apenas armazene dados limpos e prontos para agregação analítica.

### 2. Idempotência na Camada de Carga (UPSERT)
* **Decisão:** Implementei carregamento estritamente idempotente através da cláusula `ON CONFLICT (global_id_local, forecast_date) DO UPDATE SET ...` usando a pseudo-tabela `EXCLUDED`.
* **Justificação:** Em ambientes de produção, falhas de rede e tentativas automáticas de repetição (*retries*) pelo agendador são comuns. A idempotência garante que a pipeline pode ser reexecutada múltiplas vezes sem risco de duplicar linhas ou corromper métricas históricas.

### 3. Modelação: Chave Composta Natural vs Chave Substituta
* **Decisão:** Utilizei uma **Chave Primária Composta** `(global_id_local, forecast_date)`.
* **Justificação:** A identidade natural de uma previsão meteorológica é a cidade e o respetivo dia. Uma chave artificial auto-incrementada (`SERIAL`) permitiria duplicados acidentais com IDs diferentes; a chave composta transfere a garantia de unicidade para o motor relacional da base de dados.

### 4. Performance no Frontend: Caching de Queries
* **Decisão:** Utilizei o decorador `@st.cache_data(ttl=60)` no Streamlit.
* **Justificação:** Como o Streamlit reexecuta todo o script a cada interação do utilizador, a cache em memória com expiração de 60 segundos desacopla o frontend da base de dados, garantindo tempos de resposta inferiores a 50ms e poupando conexões ao PostgreSQL.

### 5. Resiliência e Isolamento de Falhas (*Graceful Degradation*)
* **Decisão:** Tratamento de exceções granular no loop da pipeline.
* **Justificação:** Se a extração de uma localidade falhar (ex: timeout temporário no IPMA para uma ilha específica), o erro é registado no log como `ERROR`, mas a pipeline continua a processar as restantes localidades com sucesso, evitando falhas em cascata.

---

## Como Executar em 60 Segundos (Docker Compose)

Não precisas de instalar Python, PostgreSQL ou bibliotecas na tua máquina. Apenas precisas do [Docker](https://www.docker.com/) instalado.

```bash
# 1. Clona o repositório
git clone https://github.com/jlevandeira/portugal-weather-data-pipeline.git
cd portugal-weather-data-pipeline

# 2. Inicializa o ecossistema completo (PostgreSQL + Dashboard + Scheduler)
docker compose up -d --build
```

Acede no teu browser a: **http://localhost:8501**

Para parar todos os containers:
```bash
docker compose down
```

---

## Qualidade de Código e Testes Automatizados

Os testes unitários validam a lógica de transformação com dados simulados (*fixtures*), sem dependência de internet:

```bash
# Correr testes localmente
pytest tests/ -v
```

A cada `git push`, o **GitHub Actions** executa automaticamente a suite de testes numa máquina virtual Ubuntu para garantir que não existem regressões de código.

---

## Estrutura do Projeto

```text
├── .github/workflows/ci.yml   # Pipeline de Integração Contínua (CI)
├── app.py                     # Dashboard analítico em Streamlit
├── docker-compose.yml         # Orquestração dos 3 containers (DB, App, Scheduler)
├── Dockerfile                 # Definição da imagem Python da aplicação
├── requirements.txt           # Dependências do projeto
├── scripts/
│   ├── scheduler.py           # Agendador periódico da pipeline
│   └── explore_api.py         # Script exploratório inicial da API
├── src/
│   ├── database.py            # Gestão de conexões e pool com SQLAlchemy
│   ├── extract.py             # Extração HTTP com timeouts defensivos
│   ├── transform.py           # Limpeza, validação de schema e enriquecimento
│   ├── load.py                # Modelação DDL e UPSERT idempotente
│   ├── logger.py              # Logging estruturado com rotação de ficheiros
│   └── pipeline.py            # Orquestrador do fluxo ETL
└── tests/
    └── test_transform.py      # Testes unitários com pytest
```

---

## Autor

Desenvolvido por **João Levandeira**  
* Licenciado em Computer Science
