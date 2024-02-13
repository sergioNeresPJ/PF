import os
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.exceptions import CouchbaseException
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Adiciona suporte a CORS ao aplicativo
# Configurando o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Obtenha as variáveis de ambiente para conexão com o Couchbase
COUCHBASE_HOST = os.environ.get('COUCHBASE_HOST')
COUCHBASE_USERNAME = os.environ.get('COUCHBASE_USERNAME')
COUCHBASE_PASSWORD = os.environ.get('COUCHBASE_PASSWORD')
COUCHBASE_BUCKET = os.environ.get('COUCHBASE_BUCKET')

print(f"COUCHBASE_HOST: {COUCHBASE_HOST}, COUCHBASE_USERNAME: {COUCHBASE_USERNAME}, COUCHBASE_PASSWORD: {COUCHBASE_PASSWORD}, COUCHBASE_BUCKET: {COUCHBASE_BUCKET}")

global bucket, cluster

# Função para verificar a conexão com o Couchbase e criar o bucket se não existir
def check_couchbase_connection():
    global bucket, cluster
    try:
        cluster = Cluster.connect(f'couchbase://{COUCHBASE_HOST}', ClusterOptions(PasswordAuthenticator(COUCHBASE_USERNAME, COUCHBASE_PASSWORD)))

        bucket = cluster.bucket(COUCHBASE_BUCKET)
        print("Conexão com o Couchbase estabelecida com sucesso!")

        return True
    except CouchbaseException as e:
        print("Erro ao conectar ao Couchbase:", str(e))
        return False


# Verifica a conexão com o Couchbase ao iniciar o aplicativo
if not check_couchbase_connection():
    exit(1)


# Função para calcular a potência
def calculate_power(a, b, microservice):
    global bucket
    try:
        # Casting para inteiros
        a = int(a)
        b = int(b)

        result = a ** b  # Calcula a potência de a elevado a b

        # Obtém o timestamp atual
        timestamp = datetime.now()

        # Insere os dados no Couchbase
        key = f"{timestamp}-{a}-{b}"
        document = {
            'timestamp': timestamp.isoformat(),
            'a': a,
            'b': b,
            'resultado': result,
            'microservice': microservice
        }
        bucket.default_collection().upsert(key, document)

        return document, 200

    except Exception as e:
        return {'error': str(e)}, 500


# Rota para processar solicitações POST
@app.route('/calculate_power', methods=['POST'])
def handle_post():
    request_data = request.json
    a = request_data.get('x')
    b = request_data.get('y')
    microservice = 'A'

    if a is None or b is None:
        return jsonify({'error': 'Missing parameters x or y'}), 400
    else:
        return jsonify(calculate_power(a, b, microservice))



# Rota para obter todos os registros
@app.route('/records', methods=['GET'])
def get_records():
    global bucket, cluster
    records = []
    query_statement = f"SELECT * FROM `{bucket.name}`"
    logger.info(f"Query Statement: {query_statement}")  # Log da consulta executada
    try:
        # Executar a consulta para obter todos os registros do bucket
        result = cluster.query(query_statement)
        logger.info("Consulta executada com sucesso.")  # Log da consulta bem-sucedida
        # Iterar sobre os resultados da consulta e adicionar os registros à lista
        for row in result.rows():
            records.append(row)

        logger.info("Registros recuperados com sucesso.")  # Log de sucesso ao recuperar registros

        # Retornar os registros como JSON
        return records, 200

    except Exception as e:
        # Lidar com qualquer outra exceção não prevista
        logger.error(f"Erro ao recuperar registros: {str(e)}")  # Log de erro ao recuperar registros

        # Retornar uma resposta de erro genérica
        return jsonify({'error': 'Erro inesperado ao recuperar registros'}), 500



# Rota de verificação de saúde
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
