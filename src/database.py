"""
Módulo de Gestão da Conexão à Base de Dados
Utiliza SQLAlchemy para gerir o connection pool ao PostgreSQL.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Carrega variáveis do ficheiro .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_secret")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "weather_db")

def get_database_url() -> str:
    """Gera a Connection String padrão para PostgreSQL com psycopg2."""
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine() -> Engine:
    """Cria e retorna a Engine de ligação do SQLAlchemy."""
    url = get_database_url()
    return create_engine(url, pool_pre_ping=True)
