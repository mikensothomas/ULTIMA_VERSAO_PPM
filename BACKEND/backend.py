# backend.py
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import queue
import random
import time
from faker import Faker
from datetime import date, timedelta

app = Flask(__name__)

dados_falsos = Faker('pt_BR')

# Filas para simulação
fila_entrada = queue.Queue()
fila_saida = queue.Queue()
filas_processamento = [queue.Queue(maxsize=3) for _ in range(4)]
contadores_filas = [0] * 4

# Função para gerar dados de passagem
def gerar_dados_passagem(id):
    data_atual = date.today()
    dias_aleatorios = random.randrange(365)
    data_em_texto = (data_atual + timedelta(days=dias_aleatorios)).strftime("%d/%m/%Y")
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
    for _ in range(50):
        dados_passagem = gerar_dados_passagem(id)
        fila_entrada.put(dados_passagem)
        id += 1
        time.sleep(0.01)

def distribuir_demandas():
    idx = 0
    while True:
        if not fila_entrada.empty():
            dados = fila_entrada.get()
            fila_entrada.task_done()
            filas_processamento[idx].put(dados)
            contadores_filas[idx] += 1
            idx = (idx + 1) % 4
        time.sleep(1)

def liberar_fila(fila, fila_saida, index):
    while True:
        if not fila.empty():
            dados = fila.get()
            fila.task_done()
            fila_saida.put(dados)
            contadores_filas[index] -= 1
        time.sleep(10)

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
        threading.Thread(target=liberar_fila, args=(fila, fila_saida, i), daemon=True).start()

    # Iniciar o servidor Flask
    app.run(host='0.0.0.0', port=5000)