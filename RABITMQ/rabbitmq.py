# import pika
# import json
# from datetime import datetime

# # Configuração da conexão com o RabbitMQ
# def conectar_rabbitmq():
#     try:
#         connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
#         channel = connection.channel()
#         # Declarar as filas para cada tipo (entrada, processamento, saída)
#         channel.queue_declare(queue='fila_entrada')
#         channel.queue_declare(queue='fila_processamento_1')
#         channel.queue_declare(queue='fila_processamento_2')
#         channel.queue_declare(queue='fila_processamento_3')
#         channel.queue_declare(queue='fila_processamento_4')
#         channel.queue_declare(queue='fila_saida')
#         return connection, channel
#     except Exception as e:
#         print("Erro ao conectar ao RabbitMQ:", e)
#         return None, None

# # Função para enviar dados para uma fila do RabbitMQ
# def enviar_para_fila(channel, fila, dados):
#     try:
#         message = json.dumps(dados)
#         channel.basic_publish(exchange='', routing_key=fila, body=message)
#         print(f"Mensagem enviada para a fila '{fila}': {dados}")
#     except Exception as e:
#         print(f"Erro ao enviar para a fila '{fila}':", e)

# # Testando o envio de dados para cada fila
# if __name__ == "__main__":
#     connection, channel = conectar_rabbitmq()
#     if channel:
#         # Teste de mensagens para cada fila
#         exemplo_dados = {
#             "ID": 1,
#             "nome": "Teste de Nome",
#             "cpf": "123.456.789-00",
#             "data": datetime.now().strftime("%Y-%m-%d"),
#             "hora": datetime.now().strftime("%H:%M:%S"),
#             "assento": 1
#         }
        
#         # Enviando para a fila de entrada
#         enviar_para_fila(channel, 'fila_entrada', exemplo_dados)
        
#         # Enviando para as filas de processamento
#         for i in range(1, 5):
#             enviar_para_fila(channel, f'fila_processamento_{i}', exemplo_dados)
        
#         # Enviando para a fila de saída
#         enviar_para_fila(channel, 'fila_saida', exemplo_dados)
        
#         # Fechar a conexão
#         connection.close()

import pika
import threading
import queue
import random
import json
from datetime import date, timedelta
import time

# Configurações e filas locais para simulação
fila_entrada = queue.Queue()
fila_saida = queue.Queue()
filas_processamento = [queue.Queue(maxsize=10)]
contadores_filas = [0]
RABBITMQ_HOST = 'rabbitmq'

# Conectar e definir canal RabbitMQ
def conectar_rabbitmq():
    credentials = pika.PlainCredentials('usuario', '12345')
    parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    return pika.BlockingConnection(parameters)

def enviar_para_fila_rabbitmq(channel, fila, dados):
    try:
        message = json.dumps(dados)
        channel.basic_publish(exchange='', routing_key=fila, body=message)
    except Exception as e:
        print(f"Erro ao enviar para a fila '{fila}':", e)

# Função para monitorar e ajustar as filas de processamento conforme a demanda
def ajustar_filas_processamento():
    demandas_na_entrada = fila_entrada.qsize()
    filas_necessarias = demandas_na_entrada // 10 + 1

    while len(filas_processamento) < filas_necessarias:
        nova_fila = queue.Queue(maxsize=10)
        filas_processamento.append(nova_fila)
        contadores_filas.append(0)
        idx = len(filas_processamento)
        
        # Criar a nova fila no RabbitMQ
        connection, channel = conectar_rabbitmq()
        channel.queue_declare(queue=f'fila_processamento_{idx}')
        print(f"Criada nova fila de processamento: fila_processamento_{idx}")
        
        # Iniciar thread para monitorar essa fila
        threading.Thread(target=liberar_fila, args=(nova_fila, idx - 1, channel), daemon=True).start()

    while len(filas_processamento) > filas_necessarias:
        fila_removida = filas_processamento.pop()
        idx = len(filas_processamento) + 1
        
        # Remover fila do RabbitMQ
        connection, channel = conectar_rabbitmq()
        channel.queue_delete(queue=f'fila_processamento_{idx}')
        print(f"Removida a fila de processamento: fila_processamento_{idx}")

        contadores_filas.pop()

def liberar_fila(fila, index, channel):
    while True:
        if not fila.empty():
            dados = fila.get()
            dados_completos = completar_dados_passagem(dados)
            enviar_para_fila_rabbitmq(channel, 'fila_saida', dados_completos)
            contadores_filas[index] -= 1
        time.sleep(2)

# Thread para monitorar e ajustar as filas continuamente
def monitorar_filas():
    while True:
        ajustar_filas_processamento()
        time.sleep(2)

# Função principal
if __name__ == "__main__":
    threading.Thread(target=monitorar_filas, daemon=True).start()