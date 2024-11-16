import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QProgressBar, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
from PyQt5.QtCore import QTimer

class PassagensUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulação de Compra e Pesquisa de Passagens Aéreas")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.label_contador_entrada = QLabel("Demandas na Fila de Entrada: 0")
        main_layout.addWidget(self.label_contador_entrada)

        self.tabela_entrada = QTableWidget()
        self.tabela_entrada.setColumnCount(3)
        self.tabela_entrada.setHorizontalHeaderLabels(["ID", "Nome", "CPF"])
        self.tabela_entrada.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        entrada_scroll = QScrollArea()
        entrada_scroll.setWidget(self.tabela_entrada)
        entrada_scroll.setWidgetResizable(True)
        entrada_scroll.setFixedHeight(150)
        main_layout.addWidget(QLabel("Fila de Entrada"))
        main_layout.addWidget(entrada_scroll)

        self.barras_filas = []
        self.labels_filas = []
        self.num_filas_processamento = 0

        self.label_contador_saida = QLabel("Demandas na Fila de Saída: 0")
        main_layout.addWidget(self.label_contador_saida)

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

        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_interface)
        self.timer.start(500)

    def atualizar_interface(self):
        try:
            resposta = requests.get("http://localhost:5000/filas")
            estado = resposta.json()

            self.label_contador_entrada.setText(f"Demandas na Fila de Entrada: {estado['contador_fila_entrada']}")

            self.tabela_entrada.setRowCount(len(estado["fila_entrada"]))
            for i, item in enumerate(estado["fila_entrada"]):
                self.tabela_entrada.setItem(i, 0, QTableWidgetItem(str(item["ID"])))
                self.tabela_entrada.setItem(i, 1, QTableWidgetItem(item["nome"]))
                self.tabela_entrada.setItem(i, 2, QTableWidgetItem(item["cpf"]))

            num_filas = len(estado["filas_processamento"])
            if num_filas > self.num_filas_processamento:
                for i in range(self.num_filas_processamento, num_filas):
                    barra = QProgressBar()
                    barra.setMaximum(10)
                    barra.setValue(0)
                    label = QLabel(f"Fila de Processamento {i+1} - Demandas: 0")
                    self.centralWidget().layout().addWidget(label)
                    self.centralWidget().layout().addWidget(barra)
                    self.labels_filas.append(label)
                    self.barras_filas.append(barra)
                self.num_filas_processamento = num_filas

            elif num_filas < self.num_filas_processamento:
                for i in range(self.num_filas_processamento - 1, num_filas - 1, -1):
                    label = self.labels_filas.pop()
                    barra = self.barras_filas.pop()
                    label.deleteLater()
                    barra.deleteLater()
                self.num_filas_processamento = num_filas

            for i, fila in enumerate(estado["filas_processamento"]):
                self.barras_filas[i].setValue(len(fila))
                self.labels_filas[i].setText(f"Fila de Processamento {i+1} - Demandas: {estado['contadores_filas'][i]}")

            self.label_contador_saida.setText(f"Demandas na Fila de Saída: {estado['contador_fila_saida']}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = PassagensUI()
    janela.show()
    sys.exit(app.exec_())