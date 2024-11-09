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

# Variável para manter threads de consumidores
consumidor_threads = []
lock = threading.Lock()

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

# Função para completar os dados com data, hora e assento
def completar_dados_passagem(dados):
    data_atual = date.today()
    dias_aleatorios = random.randrange(365)
    dados["data"] = (data_atual + timedelta(days=dias_aleatorios)).strftime("%Y-%m-%d")
    dados["hora"] = time.strftime("%H:%M:%S", time.gmtime(random.randint(0, 86400)))
    dados["assento"] = random.randint(1, 100)
    return dados

# Função para monitorar e ajustar as filas de processamento conforme a demanda
def ajustar_filas_processamento():
    demandas_na_entrada = fila_entrada.qsize()
    filas_necessarias = max(1, demandas_na_entrada // 10 + 1)  # Sempre mantém pelo menos 1 fila

    with lock:
        # Adiciona novas filas de processamento, se necessário
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
            consumidor_thread = threading.Thread(target=liberar_fila, args=(nova_fila, idx - 1, channel), daemon=True)
            consumidor_threads.append(consumidor_thread)
            consumidor_thread.start()

        # Remove filas de processamento quando a demanda diminui
        while len(filas_processamento) > filas_necessarias:
            idx = len(filas_processamento)
            fila_para_remover = filas_processamento.pop()
            contadores_filas.pop()
            consumidor_thread = consumidor_threads.pop()

            # Finalizar a thread do consumidor para a fila removida
            consumidor_thread.join()

            # Remover fila do RabbitMQ
            connection, channel = conectar_rabbitmq()
            channel.queue_delete(queue=f'fila_processamento_{idx}')
            print(f"Removida a fila de processamento: fila_processamento_{idx}")

def distribuir_demandas():
    idx = 0
    while True:
        if not fila_entrada.empty():
            with lock:
                dados = fila_entrada.get()
                fila = filas_processamento[idx]
                fila.put(dados)
                print(f"Demanda ID {dados['ID']} distribuída para fila de processamento {idx + 1}")

                # Atualiza o índice para distribuir uniformemente entre as filas
                idx = (idx + 1) % len(filas_processamento)
        elif fila_entrada.empty() and all(f.empty() for f in filas_processamento):
            # Finaliza a distribuição quando todas as filas estão vazias
            print("Todas as demandas foram processadas e distribuídas.")
            break
        time.sleep(1)  # Intervalo entre verificações

def liberar_fila(fila, index, channel):
    while True:
        with lock:
            if not fila.empty():
                dados = fila.get()
                dados_completos = completar_dados_passagem(dados)
                enviar_para_fila_rabbitmq(channel, 'fila_saida', dados_completos)
                contadores_filas[index] -= 1
            elif fila_entrada.empty() and all(f.empty() for f in filas_processamento):
                # Finaliza o loop se todas as filas de entrada e processamento estão vazias
                break
        time.sleep(2)

# Thread para monitorar e ajustar as filas continuamente
def monitorar_filas():
    while True:
        if fila_entrada.empty() and all(f.empty() for f in filas_processamento):
            print("Todas as demandas foram processadas, encerrando monitoramento.")
            break  # Encerra a thread de monitoramento quando tudo está vazio
        ajustar_filas_processamento()
        time.sleep(2)

# Função principal
if __name__ == "__main__":
    # Preenchendo a fila de entrada para simulação
    for i in range(50):  # Exemplo: 50 demandas
        fila_entrada.put({
            "ID": i + 1,
            "nome": f"Cliente {i + 1}",
            "cpf": f"123.456.789-{i:02d}"
        })

    # Iniciar threads para monitorar, distribuir e processar filas
    threading.Thread(target=monitorar_filas, daemon=True).start()
    threading.Thread(target=distribuir_demandas, daemon=True).start()
