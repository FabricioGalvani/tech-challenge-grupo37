from flask import Flask, request, jsonify, render_template
import mlflow
import mlflow.keras
import awswrangler as wr
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
import joblib

app = Flask(__name__)


@app.route('/test-aws', methods=['GET'])
def test_aws():
    import awswrangler as wr
    try:
        buckets = wr.s3.list_buckets()
        return jsonify({"buckets": buckets})
    except Exception as e:
        return jsonify({"error": str(e)})


def get_latest_run_id(experiment_name):
    # Obter o experimento pelo nome
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
        raise ValueError(f"Experimento '{experiment_name}' não encontrado.")

    experiment_id = experiment.experiment_id

    # Buscar os runs do experimento
    client = mlflow.tracking.MlflowClient()
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        order_by=["start_time DESC"],
        max_results=1  # Buscar apenas o run mais recente
    )

    if not runs:
        raise ValueError(f"Nenhum run encontrado para o experimento '{experiment_name}'.")

    # Retornar o ID do run mais recente
    return runs[0].info.run_id


# Função para carregar o modelo e o scaler do MLflow
def load_model_and_scaler(run_id):
    # Caminho do modelo e scaler no MLflow
    model_uri = f"runs:/{run_id}/lstm_petr4_model"
    scaler_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="scaler.pkl")
    
    # Carregar o scaler e o modelo
    scaler = joblib.load(scaler_path)
    model = mlflow.keras.load_model(model_uri)
    
    return model, scaler


# Página inicial com o formulário
@app.route('/')
def index():
    return render_template('upload.html')


# Rota para processar o arquivo CSV e fazer previsões
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Arquivo não selecionado"}), 400
    
    # Processar o CSV
    try:
        mlflow.set_tracking_uri("http://127.0.0.1:5000")
        mlflow.set_experiment("LSTM PETR4 Regression")

        # Ler o arquivo CSV em um DataFrame
        df = pd.read_csv(file)
        
        # Validar se a coluna 'Close' está presente
        if 'Close' not in df.columns:
            return jsonify({"error": "'Close' column is required in the CSV"}), 400

        # Exibir os valores da coluna 'Close'
        close_values = df['Close'].tolist()

        # Obter o Run ID mais recente do experimento
        experiment_name = "LSTM PETR4 Regression"
        run_id = get_latest_run_id(experiment_name)

        # Carregar o modelo e o scaler
        model, scaler = load_model_and_scaler(run_id)

        # Escalar os dados
        scaled_data = scaler.transform(df[['Close']])
    
        # Criar sequências para previsão
        sequence_length = 20
        X = []
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i, 0])

        if len(X) <= 0:
            return jsonify({"error": "Dados insuficientes para o sequence_length escolhido."}), 400
        
        X = np.array(X)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))  # [amostras, passos de tempo, features]

        #return jsonify({"close_values": close_values})
        # Fazer previsões
        predicted_prices = model.predict(X)

        # Reverter a escala para os valores originais
        predicted_prices = scaler.inverse_transform(predicted_prices)

        # Formatar em DataFrame para exibição
        df_predictions = pd.DataFrame(predicted_prices, columns=["Previsão"])
        df_predictions.index += 1  # Ajustar índice para começar em 1

        # Renderizar o HTML com as previsões
        return render_template('predictions.html', table=df_predictions.to_html(classes='table table-striped', header=True, index=True))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Função de treinamento
def train_lstm_model():
    # Configurar o servidor MLflow
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("LSTM PETR4 Regression")

    # Caminho do bucket S3
    silver_path = "s3://tech-challenge-datalake-silver/market-data/ticker/PETR4_SA/"
    
    # Ler dados do S3
    data = wr.s3.read_parquet(path=silver_path, dataset=True)

    # Usar apenas a coluna 'Close'
    data = data[['Close']]

    # Escalar os dados
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Criar sequências de entrada e saída
    sequence_length = 60
    X, y = [], []
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)

    # Redimensionar X para [amostras, passos de tempo, features]
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Dividir os dados em treino e teste
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Treinar e registrar o modelo no MLflow
    with mlflow.start_run():
        # Definir o modelo
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')

        # Log dos parâmetros
        mlflow.log_param("sequence_length", sequence_length)
        mlflow.log_param("units", 50)
        mlflow.log_param("dropout_rate", 0.2)
        mlflow.log_param("optimizer", "adam")

        # Treinar o modelo
        history = model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)

        # Logar as métricas de treino
        for epoch, loss in enumerate(history.history['loss']):
            mlflow.log_metric("train_loss", loss, step=epoch)

        # Fazer previsões para validação
        predicted_prices = model.predict(X_test)

        # Avaliar o modelo (RMSE)
        y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
        predicted_prices_actual = scaler.inverse_transform(predicted_prices)
        rmse = np.sqrt(mean_squared_error(y_test_actual, predicted_prices_actual))
        mlflow.log_metric("rmse", rmse)

        # Log do modelo treinado
        mlflow.keras.log_model(model, "lstm_petr4_model")

        # Salvar o scaler como artefato
        scaler_path = "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        mlflow.log_artifact(scaler_path)

        return {"rmse": rmse, "status": "Modelo treinado e registrado no MLflow"}



@app.route('/train', methods=['POST', 'GET'])
def train_model():
    try:
        # Chamar a função de treinamento
        result = train_lstm_model()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
