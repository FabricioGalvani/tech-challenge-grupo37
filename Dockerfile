# Use uma imagem base Python
FROM python:3.9-slim


# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*


# Instale as dependências do Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar arquivos de credenciais para o contêiner
# Suponha que o diretório ~/.aws esteja no mesmo nível do Dockerfile
COPY .aws /root/.aws

# Copiar o arquivo .env para o contêiner
COPY .env /app/.env

# Exportar variáveis do .env como variáveis de ambiente
RUN export $(cat /app/.env | xargs)


# Copie o código do Flask para o contêiner
COPY app /app
WORKDIR /app


# Exponha as portas Flask e MLflow
EXPOSE 8080 5000

# Definir a variável de ambiente para modo desenvolvimento
ENV FLASK_ENV=development


# Comando para rodar o Flask e MLflow simultaneamente
CMD ["sh", "-c", "mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts & python app.py"]
