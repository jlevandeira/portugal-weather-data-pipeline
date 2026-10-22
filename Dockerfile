# 1. Imagem base leve e oficial de Python
FROM python:3.10-slim

# Evita que o Python crie ficheiros .pyc e força logs em tempo real sem buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Define a pasta de trabalho dentro do container
WORKDIR /app

# 3. Instala dependências do sistema necessárias para compilar pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copia e instala primeiro os requirements (aproveita a cache de camadas do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copia o restante código do projeto
COPY . .

# 6. Expõe a porta padrão do Streamlit
EXPOSE 8501

# 7. Comando padrão: arranca o Streamlit com ligação externa permitida
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]