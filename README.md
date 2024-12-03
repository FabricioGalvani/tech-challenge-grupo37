# tech-challenge-grupo37
Repositório dedicado a armazenar os projetos desenvolvidos na pós de Machine Learning Engineering.

# Previsão de Preços Futuros - PETR4

Este projeto utiliza **Flask** para criar uma API que realiza previsões de preços futuros da ação **PETR4** com base em um modelo **LSTM** treinado e registrado no **MLflow**. O modelo utiliza dados carregados de arquivos CSV enviados pelo usuário. 

Além disso, o projeto é executado dentro de contêineres Docker, incluindo o **MLflow** para rastreamento de experimentos.

---

## Funcionalidades

1. **Treinamento do Modelo**:
   - A rota `/train` permite treinar um modelo LSTM com dados históricos do S3.

2. **Previsão de Preços**:
   - A rota `/upload` aceita um arquivo CSV com dados históricos e retorna os preços previstos em uma tabela HTML formatada.

3. **Integração com MLflow**:
   - Treinamento, registro do model, monitoramento e artefatos são gerenciados via MLflow.

---

## Requisitos

Antes de começar, você precisará ter instalado:

- [Docker](https://www.docker.com/)
- [Git](https://git-scm.com/)

---

## Estrutura do Projeto
    |-- project/
        |-- app/
            |-- app.py               # Código principal do Flask
            |-- templates/           # Templates HTML para renderização
                |-- upload.html      # Página para upload do CSV
                |-- predictions.html # Página para exibição das previsões
    |-- Dockerfile               # Configuração do Docker para Flask
    |-- requirements.txt         # Dependências do projeto
    |-- docker-compose.yml       # Configuração do Docker Compose para Flask e MLflow
    |-- README.md                # Documentação do projeto



## Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/tech-challenge-grupo37.git
cd tech-challenge-grupo37

