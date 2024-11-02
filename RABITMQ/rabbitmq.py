import pika
import json
from datetime import datetime

# Configuração da conexão com o RabbitMQ
def conectar_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        # Declarar as filas para cada tipo (entrada, processamento, saída)
        channel.queue_declare(queue='fila_entrada')
        channel.queue_declare(queue='fila_processamento_1')
        channel.queue_declare(queue='fila_processamento_2')
        channel.queue_declare(queue='fila_processamento_3')
        channel.queue_declare(queue='fila_processamento_4')
        channel.queue_declare(queue='fila_saida')
        return connection, channel
    except Exception as e:
        print("Erro ao conectar ao RabbitMQ:", e)
        return None, None

# Função para enviar dados para uma fila do RabbitMQ
def enviar_para_fila(channel, fila, dados):
    try:
        message = json.dumps(dados)
        channel.basic_publish(exchange='', routing_key=fila, body=message)
        print(f"Mensagem enviada para a fila '{fila}': {dados}")
    except Exception as e:
        print(f"Erro ao enviar para a fila '{fila}':", e)

# Testando o envio de dados para cada fila
if __name__ == "__main__":
    connection, channel = conectar_rabbitmq()
    if channel:
        # Teste de mensagens para cada fila
        exemplo_dados = {
            "ID": 1,
            "nome": "Teste de Nome",
            "cpf": "123.456.789-00",
            "data": datetime.now().strftime("%Y-%m-%d"),
            "hora": datetime.now().strftime("%H:%M:%S"),
            "assento": 1
        }
        
        # Enviando para a fila de entrada
        enviar_para_fila(channel, 'fila_entrada', exemplo_dados)
        
        # Enviando para as filas de processamento
        for i in range(1, 5):
            enviar_para_fila(channel, f'fila_processamento_{i}', exemplo_dados)
        
        # Enviando para a fila de saída
        enviar_para_fila(channel, 'fila_saida', exemplo_dados)
        
        # Fechar a conexão
        connection.close()
