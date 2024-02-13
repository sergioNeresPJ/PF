from flask import Flask, request, jsonify
import requests
import threading
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Adiciona suporte a CORS ao aplicativo

balanceador = True

service_ports = [
    {'name': 'serviceA', 'container_name': 'meu-servico-python' ,'port': 8081, 'available': True},
    {'name': 'serviceAPrime','container_name': 'meu-segundo-servico-python', 'port': 8082, 'available': True}
]

import logging

# Configurar o logger
logging.basicConfig(level=logging.INFO)  # Configura o nível de log para INFO

def heartbeat():
    while True:
        for service in service_ports:
            try:
                response = requests.get(f'http://{service["container_name"]}:{service["port"]}/health')
                if response.status_code == 200:
                    service['available'] = True
                else:
                    service['available'] = False
            except requests.exceptions.RequestException as e:
                # Captura exceções específicas de requests
                service['available'] = False
                logging.error(f"Erro de conexão com {service['name']}: {e}")  # Log de erro de conexão

        # Log de verificação das variáveis
        logging.info(f"Variáveis de serviço atualizadas: {service_ports}")

        time.sleep(10)

heartbeat_thread = threading.Thread(target=heartbeat)
heartbeat_thread.daemon = True
heartbeat_thread.start()


# Configure o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/records', methods=['GET'])
def handle_get():
    global balanceador
    service_url = ''

    if balanceador:
        if service_ports[0]['available']:
            service_url = f'http://{service_ports[0]["container_name"]}:{service_ports[0]["port"]}'
        else:
            service_url = f'http://{service_ports[1]["container_name"]}:{service_ports[1]["port"]}'
    else:
        if service_ports[1]['available']:
            service_url = f'http://{service_ports[0]["container_name"]}:{service_ports[1]["port"]}'
        else:
            service_url = f'http://{service_ports[1]["container_name"]}:{service_ports[0]["port"]}' 
            
    # Adicionando logs para variáveis
    logging.info(f"Valor de balanceador: {balanceador}")
    logging.info(f"Valor de service_ports: {service_ports}")
    logging.info(f"Valor de service_url: {service_url}")       

    try:
        service_url += '/records'
        response = requests.get(service_url)
        # Log para verificar a resposta recebida
        logger.info('Resposta recebida do serviço de registros: %s', response)
        response.raise_for_status()  # Lança uma exceção se a resposta indicar um erro HTTP

        # Adicione um log para imprimir o conteúdo da resposta JSON
        logger.info('Conteúdo da resposta JSON: %s', response.json())
        balanceador = (not balanceador)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        logger.error('Erro ao fazer solicitação para o serviço de registros: %s', e)
        return jsonify({'error': str(e)}), 500



@app.route('/calculate_power', methods=['POST'])
def handle_post():
    global balanceador
    
    
    service_url = ''
    
    if balanceador:
        if service_ports[0]['available']:
            service_url = f'http://{service_ports[0]["container_name"]}:{service_ports[0]["port"]}'
        else:
            service_url = f'http://{service_ports[1]["container_name"]}:{service_ports[1]["port"]}'
    else:
        if service_ports[1]['available']:
            service_url = f'http://{service_ports[1]["container_name"]}:{service_ports[1]["port"]}'
        else:
            service_url = f'http://{service_ports[0]["container_name"]}:{service_ports[0]["port"]}'        

    # Adicionando logs para variáveis
    logging.info(f"Valor de balanceador: {balanceador}")
    logging.info(f"Valor de service_ports: {service_ports}")
    logging.info(f"Valor de service_url: {service_url}")
    
    try:
        service_url += '/calculate_power'
        response = requests.post(service_url, json=request.json)
        response.raise_for_status()# Lança uma exceção se a resposta indicar um erro HTTP
        balanceador = ( not balanceador)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
