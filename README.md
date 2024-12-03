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
        |-- arquivo/
            |-- petr4_teste.csv      # Arquivo de teste e exemplo utilizado para fazer as previsões com o modelo
        |-- etl/
            |-- ingestion_market_data_bronze.py      # Arquivo utilizado para ingerir os dados no s3 na camada bronze do DataLake
            |-- ingestion_market_data_silver.py      # Arquivo utilizado para ingerir os dados no s3 na camada silver do DataLake
        |-- Dockerfile               # Configuração do Docker para Flask
        |-- requirements.txt         # Dependências do projeto
        |-- docker-compose.yml       # Configuração do Docker Compose para Flask e MLflow
        |-- README.md                # Documentação do projeto




## Configuração

### 1. Clone o Repositório

```
git clone https://github.com/seu-usuario/tech-challenge-grupo37.git
cd tech-challenge-grupo37
```

### 2. Configuração das Credenciais da AWS
O projeto utiliza awswrangler para acessar dados do S3. Para que isso funcione, é necessário configurar as credenciais da AWS.

#### a. Usando ~/.aws

Certifique-se de que o diretório ~/.aws no seu sistema contém os arquivos credentials e config com suas credenciais e configs.

Arquivo ~/.aws/credentials:
```
[default]
aws_access_key_id=SEU_ACCESS_KEY
aws_secret_access_key=SEU_SECRET_KEY
```

Arquivo ~/.aws/config:
```
[default]
region=SEU_REGION
```

### 3. Construção e Execução com Docker
Estes possos:

Constrói e executa os serviços Flask e MLflow.

Mapeia as portas:

    8080: API Flask
    
    5000: Interface do MLflow
#### a. Construir a Imagem Docker
Execute o comando abaixo para construir a imagem Docker:
```
docker build -t flask-ml-app .
```

#### a. Executar o Container
Execute o comando abaixo executar o Container Docker:
```
docker run -p 8080:8080 -p 5000:5000 -v mlartifacts:/app/mlartifacts flask-ml-app
```


Rotas Disponíveis e Funcionalidades
| Método  | Rota | Descrição  |
| ------------- |:-------------:|-------------  |
| GET      | /     |Página inicial.  |
| POST      | /upload     |Recebe um arquivo CSV, processa os dados e exibe as previsões em HTML.  |
| POST     | /train     |Treina o modelo LSTM com dados históricos armazenados no S3.  |
| GET     | /test-aws     |	Testa a conexão com os buckets S3 configurados. (Usada para depuração).  |
