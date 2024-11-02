# from flask import Flask, jsonify
# from flask_cors import CORS
# import threading
# import queue
# import random
# import time
# import pika
# import json
# import psycopg2
# from psycopg2 import sql
# from faker import Faker
# from datetime import date, timedelta

# app = Flask(__name__)
# CORS(app)

# dados_falsos = Faker('pt_BR')

# # Filas para simulação
# fila_entrada = queue.Queue()
# fila_saida = queue.Queue()
# filas_processamento = [queue.Queue(maxsize=10) for _ in range(4)]
# contadores_filas = [0] * 4

# # Conexão com o banco de dados
# def conectar_banco():
#     try:
#         conn = psycopg2.connect(
#             host="banco",
#             database="dados_passagem",
#             user="usuario",
#             password="12345"
#         )
#         return conn
#     except Exception as e:
#         print("Erro ao conectar ao banco de dados:", e)
#         return None

# # Função para inserir no banco
# def inserir_dados_banco(dados):
#     try:
#         conn = conectar_banco()
#         if conn:
#             with conn.cursor() as cur:
#                 query = sql.SQL("""
#                     INSERT INTO dados_passagem (id, nome, cpf, data, hora, assento)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                     ON CONFLICT (id) DO NOTHING
#                 """)
#                 cur.execute(query, (
#                     dados['ID'], dados['nome'], dados['cpf'],
#                     dados['data'], dados['hora'], dados['assento']
#                 ))
#             conn.commit()
#             print(f"Registro inserido no banco para o ID {dados['ID']}")
#     except Exception as e:
#         print("Erro ao inserir dados no banco de dados:", e)
#     finally:
#         if conn:
#             conn.close()

# # Função para gerar dados de passagem
# def gerar_dados_passagem(id):
#     data_atual = date.today()
#     dias_aleatorios = random.randrange(365)
#     data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
#     return {
#         "ID": id,
#         "nome": dados_falsos.name(),
#         "cpf": dados_falsos.cpf(),
#         "data": data_em_texto,
#         "hora": dados_falsos.time(),
#         "assento": random.randint(1, 100)
#     }

# # Funções de processamento paralelo
# def demandas_recebidas():
#     id = 1
#     # while True:
#     for _ in range(50):
#         dados_passagem = gerar_dados_passagem(id)
#         fila_entrada.put(dados_passagem)
#         print(f"Adicionado na fila de entrada: ID {id}")
#         id += 1
#         time.sleep(0.5)  # Tempo reduzido para testar a inserção

# def distribuir_demandas():
#     idx = 0
#     while True:
#         if not fila_entrada.empty():
#             dados = fila_entrada.get()
#             filas_processamento[idx].put(dados)
#             contadores_filas[idx] += 1
#             print(f"Distribuído para fila de processamento {idx + 1}: ID {dados['ID']}")
#             idx = (idx + 1) % 4
#         time.sleep(1)

# def liberar_fila(fila, fila_saida, index):
#     while True:
#         if not fila.empty():
#             dados = fila.get()
#             fila_saida.put(dados)
#             contadores_filas[index] -= 1
#             print(f"Liberado para fila de saída: ID {dados['ID']}")
#             inserir_dados_banco(dados)
#         time.sleep(10)

# # Rota para obter o estado das filas
# @app.route('/filas', methods=['GET'])
# def get_filas():
#     estado = {
#         "fila_entrada": list(fila_entrada.queue),
#         "filas_processamento": [list(f.queue) for f in filas_processamento],
#         "fila_saida": list(fila_saida.queue),
#         "contadores_filas": contadores_filas
#     }
#     return jsonify(estado)

# # Iniciar threads de processamento ao iniciar o backend
# if __name__ == "__main__":
#     threading.Thread(target=demandas_recebidas, daemon=True).start()
#     threading.Thread(target=distribuir_demandas, daemon=True).start()
#     for i, fila in enumerate(filas_processamento):
#         threading.Thread(target=liberar_fila, args=(fila, fila_saida, i), daemon=True).start()

#     # Iniciar o servidor Flask
#     app.run(host='0.0.0.0', port=5000)



# from flask import Flask, jsonify
# from flask_cors import CORS
# import threading
# import queue
# import random
# import time
# import psycopg2
# from psycopg2 import sql
# import pika
# import json
# from faker import Faker
# from datetime import date, timedelta

# app = Flask(__name__)
# CORS(app)

# dados_falsos = Faker('pt_BR')

# # Filas para simulação
# fila_entrada = queue.Queue()
# fila_saida = queue.Queue()
# filas_processamento = [queue.Queue(maxsize=10) for _ in range(4)]
# contadores_filas = [0] * 4

# # Configuração do RabbitMQ
# RABBITMQ_USER = 'usuario'
# RABBITMQ_PASS = '12345'
# RABBITMQ_HOST = 'rabbitmq'  # Nome do serviço no docker-compose.yml

# # Conexão com o RabbitMQ
# def conectar_rabbitmq():
#     credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#     parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
#     return pika.BlockingConnection(parameters)

# # Função para enviar mensagens ao RabbitMQ
# def enviar_para_fila_rabbitmq(fila, mensagem):
#     try:
#         connection = conectar_rabbitmq()
#         channel = connection.channel()
#         channel.queue_declare(queue=fila, durable=True)
#         channel.basic_publish(
#             exchange='',
#             routing_key=fila,
#             body=json.dumps(mensagem),
#             properties=pika.BasicProperties(delivery_mode=2)
#         )
#         print(f"Mensagem enviada para {fila}: {mensagem}")
#         connection.close()
#     except Exception as e:
#         print(f"Erro ao enviar mensagem para {fila}: {e}")

# # Conexão com o banco de dados
# def conectar_banco():
#     try:
#         conn = psycopg2.connect(
#             host="banco",
#             database="dados_passagem",
#             user="usuario",
#             password="12345"
#         )
#         return conn
#     except Exception as e:
#         print("Erro ao conectar ao banco de dados:", e)
#         return None

# # Função para inserir no banco
# def inserir_dados_banco(dados):
#     try:
#         conn = conectar_banco()
#         if conn:
#             with conn.cursor() as cur:
#                 query = sql.SQL("""
#                     INSERT INTO dados_passagem (id, nome, cpf, data, hora, assento)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                     ON CONFLICT (id) DO NOTHING
#                 """)
#                 cur.execute(query, (
#                     dados['ID'], dados['nome'], dados['cpf'],
#                     dados['data'], dados['hora'], dados['assento']
#                 ))
#             conn.commit()
#             print(f"Registro inserido no banco para o ID {dados['ID']}")
#     except Exception as e:
#         print("Erro ao inserir dados no banco de dados:", e)
#     finally:
#         if conn:
#             conn.close()

# # Função para gerar dados de passagem
# def gerar_dados_passagem(id):
#     data_atual = date.today()
#     dias_aleatorios = random.randrange(365)
#     data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
#     return {
#         "ID": id,
#         "nome": dados_falsos.name(),
#         "cpf": dados_falsos.cpf(),
#         "data": data_em_texto,
#         "hora": dados_falsos.time(),
#         "assento": random.randint(1, 100)
#     }

# # Funções de processamento paralelo
# def demandas_recebidas():
#     id = 1
#     while True:
#     # for _ in range(50):
#         dados_passagem = gerar_dados_passagem(id)
#         fila_entrada.put(dados_passagem)
#         enviar_para_fila_rabbitmq("fila_entrada", dados_passagem)
#         print(f"Adicionado na fila de entrada: ID {id}")
#         id += 1
#         time.sleep(0.5)

# def distribuir_demandas():
#     idx = 0
#     while True:
#         if not fila_entrada.empty():
#             dados = fila_entrada.get()
#             filas_processamento[idx].put(dados)
#             enviar_para_fila_rabbitmq(f"fila_processamento_{idx+1}", dados)
#             contadores_filas[idx] += 1
#             print(f"Distribuído para fila de processamento {idx + 1}: ID {dados['ID']}")
#             idx = (idx + 1) % 4
#         time.sleep(1)

# def liberar_fila(fila, fila_saida, index):
#     while True:
#         if not fila.empty():
#             dados = fila.get()
#             fila_saida.put(dados)
#             enviar_para_fila_rabbitmq("fila_saida", dados)
#             contadores_filas[index] -= 1
#             print(f"Liberado para fila de saída: ID {dados['ID']}")
#             inserir_dados_banco(dados)
#         time.sleep(5)

# # Rota para obter o estado das filas
# @app.route('/filas', methods=['GET'])
# def get_filas():
#     estado = {
#         "fila_entrada": list(fila_entrada.queue),
#         "filas_processamento": [list(f.queue) for f in filas_processamento],
#         "fila_saida": list(fila_saida.queue),
#         "contadores_filas": contadores_filas
#     }
#     return jsonify(estado)

# # Iniciar threads de processamento ao iniciar o backend
# if __name__ == "__main__":
#     threading.Thread(target=demandas_recebidas, daemon=True).start()
#     threading.Thread(target=distribuir_demandas, daemon=True).start()
#     for i, fila in enumerate(filas_processamento):
#         threading.Thread(target=liberar_fila, args=(fila, fila_saida, i), daemon=True).start()

#     # Iniciar o servidor Flask
#     app.run(host='0.0.0.0', port=5000)

from flask import Flask, jsonify
from flask_cors import CORS
import threading
import queue
import random
import time
import psycopg2
from psycopg2 import sql
import pika
import json
from faker import Faker
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)

dados_falsos = Faker('pt_BR')

# Filas internas para simulação
fila_entrada = queue.Queue()
fila_saida = queue.Queue()
filas_processamento = [queue.Queue(maxsize=10) for _ in range(4)]
contadores_filas = [0] * 4

# Configuração do RabbitMQ
RABBITMQ_USER = 'usuario'
RABBITMQ_PASS = '12345'
RABBITMQ_HOST = 'rabbitmq'  # Nome do serviço no docker-compose.yml

# Conexão com o RabbitMQ
def conectar_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    return pika.BlockingConnection(parameters)

# Função para enviar mensagens ao RabbitMQ
def enviar_para_fila_rabbitmq(fila, mensagem):
    try:
        connection = conectar_rabbitmq()
        channel = connection.channel()
        channel.queue_declare(queue=fila, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=fila,
            body=json.dumps(mensagem),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Mensagem enviada para {fila}: {mensagem}")
        connection.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem para {fila}: {e}")

# Conexão com o banco de dados
def conectar_banco():
    try:
        conn = psycopg2.connect(
            host="banco",
            database="dados_passagem",
            user="usuario",
            password="12345"
        )
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

# Função para inserir no banco
def inserir_dados_banco(dados):
    try:
        conn = conectar_banco()
        if conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO dados_passagem (id, nome, cpf, data, hora, assento)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """)
                cur.execute(query, (
                    dados['ID'], dados['nome'], dados['cpf'],
                    dados['data'], dados['hora'], dados['assento']
                ))
            conn.commit()
            print(f"Registro inserido no banco para o ID {dados['ID']}")
    except Exception as e:
        print("Erro ao inserir dados no banco de dados:", e)
    finally:
        if conn:
            conn.close()

# Função para gerar dados de passagem
def gerar_dados_passagem(id):
    data_atual = date.today()
    dias_aleatorios = random.randrange(365)
    data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
    return {
        "ID": id,
        "nome": dados_falsos.name(),
        "cpf": dados_falsos.cpf(),
        "data": data_em_texto,
        "hora": dados_falsos.time(),
        "assento": random.randint(1, 100)
    }

# Funções de processamento paralelo
def demandas_recebidas():
    id = 1
    while True:
        dados_passagem = gerar_dados_passagem(id)
        fila_entrada.put(dados_passagem)
        enviar_para_fila_rabbitmq("fila_entrada", dados_passagem)
        print(f"Adicionado na fila de entrada: ID {id}")
        id += 1
        time.sleep(0.5)

def distribuir_demandas():
    idx = 0
    while True:
        if not fila_entrada.empty():
            dados = fila_entrada.get()
            filas_processamento[idx].put(dados)
            enviar_para_fila_rabbitmq(f"fila_processamento_{idx+1}", dados)
            contadores_filas[idx] += 1
            print(f"Distribuído para fila de processamento {idx + 1}: ID {dados['ID']}")
            idx = (idx + 1) % 4
        time.sleep(1)

def liberar_fila(fila, index):
    while True:
        if not fila.empty():
            dados = fila.get()
            fila_saida.put(dados)
            enviar_para_fila_rabbitmq("fila_saida", dados)
            contadores_filas[index] -= 1
            print(f"Liberado para fila de saída: ID {dados['ID']}")
            inserir_dados_banco(dados)
        time.sleep(5)

# Rota para obter o estado das filas
@app.route('/filas', methods=['GET'])
def get_filas():
    estado = {
        "fila_entrada": list(fila_entrada.queue),
        "filas_processamento": [list(f.queue) for f in filas_processamento],
        "fila_saida": list(fila_saida.queue),
        "contadores_filas": contadores_filas
    }
    return jsonify(estado)

# Iniciar threads de processamento ao iniciar o backend
if __name__ == "__main__":
    threading.Thread(target=demandas_recebidas, daemon=True).start()
    threading.Thread(target=distribuir_demandas, daemon=True).start()
    for i, fila in enumerate(filas_processamento):
        threading.Thread(target=liberar_fila, args=(fila, i), daemon=True).start()

    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=5000)