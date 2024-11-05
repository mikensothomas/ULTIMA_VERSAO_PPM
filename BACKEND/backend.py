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

# # Filas internas para simulação
# fila_entrada = queue.Queue()
# fila_saida = queue.Queue()
# filas_processamento = [queue.Queue(maxsize=10)]
# contadores_filas = [0]

# # Configuração do RabbitMQ
# RABBITMQ_USER = 'usuario'
# RABBITMQ_PASS = '12345'
# RABBITMQ_HOST = 'rabbitmq'

# def conectar_rabbitmq():
#     credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#     parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
#     return pika.BlockingConnection(parameters)

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
#         connection.close()
#     except Exception as e:
#         print(f"Erro ao enviar mensagem para {fila}: {e}")

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
#                     dados.get('data'), dados.get('hora'), dados.get('assento')
#                 ))
#             conn.commit()
#     except Exception as e:
#         print("Erro ao inserir dados no banco de dados:", e)
#     finally:
#         if conn:
#             conn.close()

# # Função para gerar dados iniciais (apenas ID, Nome, CPF)
# def gerar_dados_passagem_inicial(id):
#     return {
#         "ID": id,
#         "nome": dados_falsos.name(),
#         "cpf": dados_falsos.cpf()
#     }

# # Função para gerar os campos adicionais (Data, Hora, Assento) após o processamento
# def completar_dados_passagem(dados):
#     data_atual = date.today()
#     dias_aleatorios = random.randrange(365)
#     data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
#     dados["data"] = data_em_texto
#     dados["hora"] = dados_falsos.time()
#     dados["assento"] = random.randint(1, 100)
#     return dados

# def demandas_recebidas():
#     id = 1
#     while True:
#         dados_passagem = gerar_dados_passagem_inicial(id)
#         fila_entrada.put(dados_passagem)
#         enviar_para_fila_rabbitmq("fila_entrada", dados_passagem)
#         print(f"Adicionado na fila de entrada: ID {id}")
#         id += 1

#         # Checar se precisamos de uma nova fila de processamento
#         if fila_entrada.qsize() // 20 + 1 > len(filas_processamento):
#             nova_fila = queue.Queue(maxsize=10)
#             filas_processamento.append(nova_fila)
#             contadores_filas.append(0)
#             threading.Thread(target=liberar_fila, args=(nova_fila, len(filas_processamento) - 1), daemon=True).start()
#             print(f"Criada nova fila de processamento. Total de filas: {len(filas_processamento)}")

#         time.sleep(0.5)

# def distribuir_demandas():
#     idx = 0
#     while True:
#         if not fila_entrada.empty():
#             dados = fila_entrada.get()
#             fila = filas_processamento[idx]
#             fila.put(dados)
#             enviar_para_fila_rabbitmq(f"fila_processamento_{idx+1}", dados)
#             contadores_filas[idx] += 1
#             print(f"Distribuído para fila de processamento {idx + 1}: ID {dados['ID']}")
#             idx = (idx + 1) % len(filas_processamento)
#         time.sleep(1)

# def liberar_fila(fila, index):
#     while True:
#         if not fila.empty():
#             dados = fila.get()
#             dados_completos = completar_dados_passagem(dados)
#             fila_saida.put(dados_completos)
#             enviar_para_fila_rabbitmq("fila_saida", dados_completos)
#             contadores_filas[index] -= 1
#             print(f"Liberado para fila de saída: ID {dados_completos['ID']}")
#             inserir_dados_banco(dados_completos)
#         time.sleep(2)

# @app.route('/filas', methods=['GET'])
# def get_filas():
#     estado = {
#         "fila_entrada": list(fila_entrada.queue),
#         "fila_saida": list(fila_saida.queue),
#         "contadores_filas": contadores_filas,
#         "filas_processamento": [list(f.queue) for f in filas_processamento],
#         "contador_fila_entrada": fila_entrada.qsize(),
#         "contador_fila_saida": fila_saida.qsize()
#     }
#     return jsonify(estado)

# if __name__ == "__main__":
#     threading.Thread(target=demandas_recebidas, daemon=True).start()
#     threading.Thread(target=distribuir_demandas, daemon=True).start()
#     for i, fila in enumerate(filas_processamento):
#         threading.Thread(target=liberar_fila, args=(fila, i), daemon=True).start()
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

# # Filas internas para simulação
# fila_entrada = queue.Queue()
# fila_saida = queue.Queue()
# filas_processamento = [queue.Queue(maxsize=10)]
# contadores_filas = [0]

# # Configuração do RabbitMQ
# RABBITMQ_USER = 'usuario'
# RABBITMQ_PASS = '12345'
# RABBITMQ_HOST = 'rabbitmq'

# def conectar_rabbitmq():
#     credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#     parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
#     return pika.BlockingConnection(parameters)

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
#         connection.close()
#     except Exception as e:
#         print(f"Erro ao enviar mensagem para {fila}: {e}")

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
#                     dados.get('data'), dados.get('hora'), dados.get('assento')
#                 ))
#             conn.commit()
#     except Exception as e:
#         print("Erro ao inserir dados no banco de dados:", e)
#     finally:
#         if conn:
#             conn.close()

# # Função para gerar dados iniciais (apenas ID, Nome, CPF)
# def gerar_dados_passagem_inicial(id):
#     return {
#         "ID": id,
#         "nome": dados_falsos.name(),
#         "cpf": dados_falsos.cpf()
#     }

# # Função para gerar os campos adicionais (Data, Hora, Assento) após o processamento
# def completar_dados_passagem(dados):
#     data_atual = date.today()
#     dias_aleatorios = random.randrange(365)
#     data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
#     dados["data"] = data_em_texto
#     dados["hora"] = dados_falsos.time()
#     dados["assento"] = random.randint(1, 100)
#     return dados

# def demandas_recebidas():
#     id = 1
#     for _ in range(100):  # Limite de 50 demandas para teste
#         dados_passagem = gerar_dados_passagem_inicial(id)
#         fila_entrada.put(dados_passagem)
#         enviar_para_fila_rabbitmq("fila_entrada", dados_passagem)
#         print(f"Adicionado na fila de entrada: ID {id}")
#         id += 1
#         ajustar_filas_processamento()  # Ajusta o número de filas conforme necessário
#         time.sleep(0.5)

# # def ajustar_filas_processamento():
# #     # Ajustar o número de filas com base nas demandas na fila de entrada
# #     demandas_na_entrada = fila_entrada.qsize()
# #     filas_necessarias = demandas_na_entrada // 10 + 1  # 1 fila para cada 10 demandas na entrada
    
# #     # Adiciona filas se necessário
# #     while len(filas_processamento) < filas_necessarias:
# #         nova_fila = queue.Queue(maxsize=10)
# #         filas_processamento.append(nova_fila)
# #         contadores_filas.append(0)
# #         threading.Thread(target=liberar_fila, args=(nova_fila, len(filas_processamento) - 1), daemon=True).start()
# #         print(f"Criada nova fila de processamento. Total de filas: {len(filas_processamento)}")
    
# #     # Remove filas se necessário
# #     while len(filas_processamento) > filas_necessarias:
# #         fila_removida = filas_processamento.pop()
# #         contadores_filas.pop()
# #         print(f"Removida uma fila de processamento. Total de filas: {len(filas_processamento)}")

# def ajustar_filas_processamento():
#     # Ajustar o número de filas com base nas demandas na fila de entrada
#     demandas_na_entrada = fila_entrada.qsize()
#     filas_necessarias = demandas_na_entrada // 10 + 1  # 1 fila para cada 10 demandas na entrada

#     # Adiciona filas se necessário
#     while len(filas_processamento) < filas_necessarias:
#         nova_fila = queue.Queue(maxsize=10)
#         filas_processamento.append(nova_fila)
#         contadores_filas.append(0)
#         threading.Thread(target=liberar_fila, args=(nova_fila, len(filas_processamento) - 1), daemon=True).start()
#         print(f"Criada nova fila de processamento. Total de filas: {len(filas_processamento)}")
    
#     # Remove filas se necessário
#     while len(filas_processamento) > filas_necessarias:
#         fila_removida = filas_processamento.pop()
#         contadores_filas.pop()
#         print(f"Removida uma fila de processamento. Total de filas: {len(filas_processamento)}")

# def distribuir_demandas():
#     idx = 0
#     while True:
#         if not fila_entrada.empty():
#             dados = fila_entrada.get()
#             fila = filas_processamento[idx]
#             fila.put(dados)
#             enviar_para_fila_rabbitmq(f"fila_processamento_{idx+1}", dados)
#             contadores_filas[idx] += 1
#             print(f"Distribuído para fila de processamento {idx + 1}: ID {dados['ID']}")
#             idx = (idx + 1) % len(filas_processamento)
#         time.sleep(1)

# def liberar_fila(fila, index):
#     while True:
#         if not fila.empty():
#             dados = fila.get()
#             dados_completos = completar_dados_passagem(dados)
#             fila_saida.put(dados_completos)
#             enviar_para_fila_rabbitmq("fila_saida", dados_completos)
#             contadores_filas[index] -= 1
#             print(f"Liberado para fila de saída: ID {dados_completos['ID']}")
#             inserir_dados_banco(dados_completos)
#         time.sleep(2)

# @app.route('/filas', methods=['GET'])
# def get_filas():
#     estado = {
#         "fila_entrada": list(fila_entrada.queue),
#         "fila_saida": list(fila_saida.queue),
#         "contadores_filas": contadores_filas,
#         "filas_processamento": [list(f.queue) for f in filas_processamento],
#         "contador_fila_entrada": fila_entrada.qsize(),
#         "contador_fila_saida": fila_saida.qsize()
#     }
#     return jsonify(estado)

# if __name__ == "__main__":
#     threading.Thread(target=demandas_recebidas, daemon=True).start()
#     threading.Thread(target=distribuir_demandas, daemon=True).start()
#     for i, fila in enumerate(filas_processamento):
#         threading.Thread(target=liberar_fila, args=(fila, i), daemon=True).start()
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
filas_processamento = [queue.Queue(maxsize=10)]
contadores_filas = [0]

# Configuração do RabbitMQ
RABBITMQ_USER = 'usuario'
RABBITMQ_PASS = '12345'
RABBITMQ_HOST = 'rabbitmq'

def conectar_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    return pika.BlockingConnection(parameters)

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
        connection.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem para {fila}: {e}")

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
                    dados.get('data'), dados.get('hora'), dados.get('assento')
                ))
            conn.commit()
    except Exception as e:
        print("Erro ao inserir dados no banco de dados:", e)
    finally:
        if conn:
            conn.close()

def gerar_dados_passagem_inicial(id):
    return {
        "ID": id,
        "nome": dados_falsos.name(),
        "cpf": dados_falsos.cpf()
    }

def completar_dados_passagem(dados):
    data_atual = date.today()
    dias_aleatorios = random.randrange(365)
    data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
    dados["data"] = data_em_texto
    dados["hora"] = dados_falsos.time()
    dados["assento"] = random.randint(1, 100)
    return dados

def demandas_recebidas():
    id = 1
    for _ in range(110):  # Limite de 100 demandas para teste
        dados_passagem = gerar_dados_passagem_inicial(id)
        fila_entrada.put(dados_passagem)
        enviar_para_fila_rabbitmq("fila_entrada", dados_passagem)
        print(f"Adicionado na fila de entrada: ID {id}")
        id += 1
        time.sleep(0.5)

def ajustar_filas_processamento():
    demandas_na_entrada = fila_entrada.qsize()
    filas_necessarias = demandas_na_entrada // 10 + 1  # 1 fila para cada 10 demandas na entrada

    while len(filas_processamento) < filas_necessarias:
        nova_fila = queue.Queue(maxsize=10)
        filas_processamento.append(nova_fila)
        contadores_filas.append(0)
        threading.Thread(target=liberar_fila, args=(nova_fila, len(filas_processamento) - 1), daemon=True).start()
        print(f"Criada nova fila de processamento. Total de filas: {len(filas_processamento)}")

    while len(filas_processamento) > filas_necessarias:
        filas_processamento.pop()
        contadores_filas.pop()
        print(f"Removida uma fila de processamento. Total de filas: {len(filas_processamento)}")

def monitorar_filas():
    while True:
        ajustar_filas_processamento()
        time.sleep(2)  # Intervalo de monitoramento

def distribuir_demandas():
    idx = 0
    while True:
        if not fila_entrada.empty():
            dados = fila_entrada.get()
            fila = filas_processamento[idx]
            fila.put(dados)
            enviar_para_fila_rabbitmq(f"fila_processamento_{idx+1}", dados)
            contadores_filas[idx] += 1
            print(f"Distribuído para fila de processamento {idx + 1}: ID {dados['ID']}")
            idx = (idx + 1) % len(filas_processamento)
        time.sleep(1)

def liberar_fila(fila, index):
    while True:
        if not fila.empty():
            dados = fila.get()
            dados_completos = completar_dados_passagem(dados)
            fila_saida.put(dados_completos)
            enviar_para_fila_rabbitmq("fila_saida", dados_completos)
            contadores_filas[index] -= 1
            print(f"Liberado para fila de saída: ID {dados_completos['ID']}")
            inserir_dados_banco(dados_completos)
        time.sleep(2)

@app.route('/filas', methods=['GET'])
def get_filas():
    estado = {
        "fila_entrada": list(fila_entrada.queue),
        "fila_saida": list(fila_saida.queue),
        "contadores_filas": contadores_filas,
        "filas_processamento": [list(f.queue) for f in filas_processamento],
        "contador_fila_entrada": fila_entrada.qsize(),
        "contador_fila_saida": fila_saida.qsize()
    }
    return jsonify(estado)

if __name__ == "__main__":
    threading.Thread(target=demandas_recebidas, daemon=True).start()
    threading.Thread(target=distribuir_demandas, daemon=True).start()
    threading.Thread(target=monitorar_filas, daemon=True).start()
    for i, fila in enumerate(filas_processamento):
        threading.Thread(target=liberar_fila, args=(fila, i), daemon=True).start()
    app.run(host='0.0.0.0', port=5000)