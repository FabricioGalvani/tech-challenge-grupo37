import awswrangler as wr
import pandas as pd

# Caminhos dos buckets
bronze_path = "s3://tech-challenge-datalake-bronze/market-data/ticker/PETR4_SA/"
silver_path = "s3://tech-challenge-datalake-silver/market-data/ticker/PETR4_SA/"

# Ler os arquivos do bucket Bronze
data = wr.s3.read_csv(
    path=bronze_path,
    dataset=True  # Lê todos os arquivos no diretório como um único DataFrame
)

# # Remover a linha indesejada (contendo ',PETR4.SA,PETR4.SA,...')
# data = data[data['Date'] != ',PETR4.SA,PETR4.SA,PETR4.SA,PETR4.SA,PETR4.SA,PETR4.SA']

# Selecionar as colunas necessárias
data = data[['Date', 'Close', 'Open']]

# Garantir que não há valores nulos ou inválidos
data = data.dropna()

# Salvar os dados no bucket Silver
wr.s3.to_parquet(
    data,
    path=silver_path,
    index=False,
    dataset=True  # Salvar como dataset para organização eficiente no S3
)

print(f"Dados processados e salvos em {silver_path}")
