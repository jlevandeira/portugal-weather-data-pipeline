# Cábula Técnica para Entrevistas (LEARNING.md)

Este documento regista as decisões de arquitetura, conceitos teóricos e respostas a perguntas típicas de entrevistas técnicas para este projeto.

---

## Índice de Conceitos
1. [Fase 1: Setup, Boas Práticas e Arquitetura Base](#fase-1-setup-boas-práticas-e-arquitetura-base)
2. [Fase 2: Extract & Transform (ETL vs ELT, Pandas, Schemas)](#fase-2-extract--transform) *(em breve)*
3. [Fase 3: Modelação e Base de Dados (PostgreSQL, Docker, Idempotência)](#fase-3-modelação-e-base-de-dados) *(em breve)*
4. [Fase 4: Automação e Logging Estruturado](#fase-4-automação-e-logging-estruturado) *(em breve)*
5. [Fase 5: Dashboard e Apresentação de Dados](#fase-5-dashboard-e-apresentação-de-dados) *(em breve)*
6. [Fase 6: Qualidade, Testes e CI/CD](#fase-6-qualidade-testes-e-cicd) *(em breve)*
7. [Fase 7: Deploy e Produção](#fase-7-deploy-e-produção) *(em breve)*

---

## Fase 1: Setup, Boas Práticas e Arquitetura Base

### Conceitos Chave

#### 1. Separação de Responsabilidades (Separation of Concerns)
* **Conceito:** Cada módulo/camada de software tem um único propósito. Não misturamos lógica de chamada HTTP (extração) com limpeza de dados ou queries à base de dados.
* **Porquê no projeto?** Se a API do IPMA mudar a estrutura do JSON, alteramos apenas `src/extract.py`. A base de dados e o dashboard continuam intactos.
* **Como defender numa entrevista:** *"Adotei uma arquitetura modular por camadas (Extract, Transform, Load, Presentation). Isto garante desacoplamento, facilita testes unitários isolados e permite trocar componentes (ex.: mudar de PostgreSQL para Snowflake) sem reescrever o resto da aplicação."*

#### 2. Isolamento de Ambientes (`venv`)
* **Conceito:** O ambiente virtual isola as bibliotecas do projeto da instalação global do sistema operativo.
* **Alternativas consideradas:** `pipenv`, `poetry`, `uv`. Começámos com `venv` + `requirements.txt` por ser a ferramenta nativa e mais universal de Python, minimizando overhead inicial.
* **Como defender numa entrevista:** *"Garante reprodutibilidade. Qualquer colega de equipa ou pipeline de CI executa exatamente as mesmas versões de dependências sem conflitos com outros projetos."*

#### 3. Gestão de Segredos & `.env.example`
* **Conceito:** Segredos (passwords, tokens, strings de conexão) nunca entram no controlo de versão (Git).
* **Boa prática:** O ficheiro `.env` está no `.gitignore`. O repositório apenas versiona o `.env.example`, que serve de contrato/documentação das variáveis esperadas pelo sistema.
* **Como defender numa entrevista:** *"Segurança por defeito (12-Factor App methodology). As configurações variam por ambiente (desenvolvimento vs produção) e as credenciais são injetadas via variáveis de ambiente, nunca 'hardcoded'."*

---
*(Secções seguintes serão adicionadas no fim de cada fase)*
