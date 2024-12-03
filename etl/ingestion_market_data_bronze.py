import yfinance as yf
import awswrangler as wr

# Bucket S3 & Prefix
BUCKET_BRONZE = "tech-challenge-datalake-bronze"
PREFIX = "market-data/ticker/PETR4_SA"

# Símbolo da ação
SYMBOL = "PETR4.SA"

# Período desejado
PERIOD = "1y"

# Obter os dados históricos
data = yf.download(SYMBOL, period=PERIOD)

# Resetar o índice para transformar 'Date' em uma coluna
data.reset_index(inplace=True)

# Garantir que a coluna 'Date' seja uma string
data["Date"] = data["Date"].astype(str)

# Adicionar colunas de ano e mês baseadas na coluna 'Date'
data["Year"] = data["Date"].str[:4]
data["Month"] = data["Date"].str[5:7]

# Para cada ano e mês, filtrar os dados e salvar no S3
for year in data["Year"].unique():
    for month in data[data["Year"] == year]["Month"].unique():
        # Filtrar os dados para o ano e mês
        subset = data[(data["Year"] == year) & (data["Month"] == month)]
        
        # Remover as colunas 'Year' e 'Month' antes de salvar
        subset = subset.drop(columns=["Year", "Month"])
        
        # Especificar o caminho dinâmico no S3
        path = f"s3://{BUCKET_BRONZE}/{PREFIX}/year={year}/month={month}/data.csv"
        
        # Salvar o subset no S3
        wr.s3.to_csv(
            subset,
            path,
            index=False
        )
        
        print(f"Dados salvos em: {path}")
