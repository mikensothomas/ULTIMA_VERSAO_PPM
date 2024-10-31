import sys
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Modo offscreen para evitar problemas de display
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QProgressBar, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
from PyQt5.QtCore import QTimer

class PassagensUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulação de Compra e Pesquisa de Passagens Aéreas")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        main_layout = QVBoxLayout()

        # Configuração da tabela de entrada com scroll vertical
        self.tabela_entrada = QTableWidget()
        self.tabela_entrada.setColumnCount(6)
        self.tabela_entrada.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Data", "Hora", "Assento"])
        self.tabela_entrada.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        entrada_scroll = QScrollArea()
        entrada_scroll.setWidget(self.tabela_entrada)
        entrada_scroll.setWidgetResizable(True)
        entrada_scroll.setFixedHeight(150)
        main_layout.addWidget(QLabel("Fila de Entrada"))
        main_layout.addWidget(entrada_scroll)

        # Barras de progresso das filas de processamento
        self.barras_filas = []
        self.labels_filas = []
        for i in range(4):
            barra = QProgressBar()
            barra.setMaximum(10)
            barra.setValue(0)
            label = QLabel(f"Fila de Processamento {i+1} - Demandas: 0")
            main_layout.addWidget(label)
            main_layout.addWidget(barra)
            self.labels_filas.append(label)
            self.barras_filas.append(barra)

        # Configuração da tabela de saída com scroll vertical
        self.tabela_saida = QTableWidget()
        self.tabela_saida.setColumnCount(6)
        self.tabela_saida.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Data", "Hora", "Assento"])
        self.tabela_saida.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        saida_scroll = QScrollArea()
        saida_scroll.setWidget(self.tabela_saida)
        saida_scroll.setWidgetResizable(True)
        saida_scroll.setFixedHeight(150)
        main_layout.addWidget(QLabel("Fila de Saída"))
        main_layout.addWidget(saida_scroll)

        # Timer para atualização da interface
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_interface)
        self.timer.start(1000)

        # Definir layout principal
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def atualizar_interface(self):
        # Obter dados do backend
        try:
            # resposta = requests.get("http://backend:5000/filas")
            # estado = resposta.json()

            resposta = requests.get("http://backend:5000/filas")
            estado = resposta.json()
            
            # Atualizar a tabela de entrada
            self.tabela_entrada.setRowCount(len(estado["fila_entrada"]))
            for i, item in enumerate(estado["fila_entrada"]):
                self.tabela_entrada.setItem(i, 0, QTableWidgetItem(str(item["ID"])))
                self.tabela_entrada.setItem(i, 1, QTableWidgetItem(item["nome"]))
                self.tabela_entrada.setItem(i, 2, QTableWidgetItem(item["cpf"]))
                self.tabela_entrada.setItem(i, 3, QTableWidgetItem(item["data"]))
                self.tabela_entrada.setItem(i, 4, QTableWidgetItem(item["hora"]))
                self.tabela_entrada.setItem(i, 5, QTableWidgetItem(str(item["assento"])))

            # Atualizar as barras de progresso das filas de processamento
            for i, fila in enumerate(estado["filas_processamento"]):
                self.barras_filas[i].setValue(len(fila))
                self.labels_filas[i].setText(f"Fila de Processamento {i+1} - Demandas: {estado['contadores_filas'][i]}")

            # Atualizar a tabela de saída
            self.tabela_saida.setRowCount(len(estado["fila_saida"]))
            for i, item in enumerate(estado["fila_saida"]):
                self.tabela_saida.setItem(i, 0, QTableWidgetItem(str(item["ID"])))
                self.tabela_saida.setItem(i, 1, QTableWidgetItem(item["nome"]))
                self.tabela_saida.setItem(i, 2, QTableWidgetItem(item["cpf"]))
                self.tabela_saida.setItem(i, 3, QTableWidgetItem(item["data"]))
                self.tabela_saida.setItem(i, 4, QTableWidgetItem(item["hora"]))
                self.tabela_saida.setItem(i, 5, QTableWidgetItem(str(item["assento"])))
        
        except Exception as e:
            print("Erro ao obter dados do backend:", e)

# Função principal
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = PassagensUI()
    janela.show()
    sys.exit(app.exec_())
