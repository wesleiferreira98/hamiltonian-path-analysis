# src/gui/main_window.py

import sys
import os
import time
from typing import Optional, List, Tuple
from pathlib import Path


from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QTabWidget,
)
from PyQt6.QtCore import Qt, QTimer

# Logger avançado
from src.gui.logger_widget import LoggerWidget

# Corrigir PATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.graph_io import load_graph
from src.backtracking import (
    hamiltonian_path_backtracking,
    hamiltonian_path_backtracking_steps,
)
from src.heuristic import heuristic_hamiltonian_path
from src.utils.graph_generator import generate_random_graph, save_graph
#from src.experiments.graph_experiments import run_experiments

from src.gui.graph_canvas import GraphCanvas
from src.gui.comparison_window import ComparisonWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hamiltonian Path Analyzer")
        self.resize(1400, 800)

        # Estado
        self.current_n = 0
        self.current_edges = []
        self.current_path_exact = None
        self.current_path_heur = None

        # Componentes principais
        self.graph_canvas = GraphCanvas(self)
        self.logger = LoggerWidget()

        self.label_status = QLabel("Nenhum grafo carregado.")
        self.label_status.setWordWrap(True)

        # Grupo: carregamento / geração
        group_graph = QGroupBox("Grafo")
        btn_load = QPushButton("Carregar grafo de arquivo")
        btn_generate = QPushButton("Gerar grafo aleatório")

        self.spin_n = QSpinBox()
        self.spin_n.setRange(3, 200)
        self.spin_n.setValue(10)

        self.combo_density = QComboBox()
        self.combo_density.addItems(["Esparso (p=0.2)", "Médio (p=0.5)", "Denso (p=0.8)"])
        self.tabs = QTabWidget()

        layout_graph = QVBoxLayout()
        layout_graph.addWidget(btn_load)

        h_gen = QHBoxLayout()
        h_gen.addWidget(QLabel("n:"))
        h_gen.addWidget(self.spin_n)
        h_gen.addWidget(QLabel("Densidade:"))
        h_gen.addWidget(self.combo_density)

        layout_graph.addLayout(h_gen)
        layout_graph.addWidget(btn_generate)
        group_graph.setLayout(layout_graph)

        # Grupo: execução
        group_run = QGroupBox("Execução")
        btn_run_exact = QPushButton("Executar Backtracking (Exato)")
        btn_run_heur = QPushButton("Executar Heurística")
        btn_run_exact_animated = QPushButton("Animação Backtracking (Passo a Passo)")
        btn_compare = QPushButton("Comparar Exato vs Heurística")

        self.label_exact_time = QLabel("Tempo (exato): -")
        self.label_heur_time = QLabel("Tempo (heurística): -")

        layout_run = QVBoxLayout()
        layout_run.addWidget(btn_run_exact)
        layout_run.addWidget(btn_run_heur)
        layout_run.addWidget(btn_run_exact_animated)
        layout_run.addWidget(self.label_exact_time)
        layout_run.addWidget(self.label_heur_time)
        layout_run.addWidget(btn_compare)
        group_run.setLayout(layout_run)

        # Painel lateral
        side_layout = QVBoxLayout()
        side_layout.addWidget(group_graph)
        side_layout.addWidget(group_run)
        side_layout.addWidget(self.label_status)
        side_layout.addWidget(self.logger, stretch=1)

        side_widget = QWidget()
        side_widget.setLayout(side_layout)

        # Layout principal
        central = QWidget()
        layout_main = QHBoxLayout()
        layout_main.addWidget(self.graph_canvas, stretch=3)
        layout_main.addWidget(side_widget, stretch=2)
        central.setLayout(layout_main)
        self.setCentralWidget(central)

        # Timer para animação
        self.step_generator = None
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(300)
        self.animation_timer.timeout.connect(self.on_animation_step)

        # Conexões
        btn_load.clicked.connect(self.on_load_graph)
        btn_generate.clicked.connect(self.on_generate_graph)
        btn_run_exact.clicked.connect(self.on_run_exact)
        btn_run_heur.clicked.connect(self.on_run_heur)
        btn_run_exact_animated.clicked.connect(self.on_start_animation)
        btn_compare.clicked.connect(self.on_compare)
        self.load_stylesheet()



    def load_stylesheet(self):
        try:
            path = Path(__file__).parent / "resources" / "style.qss"
            with open(path, "r") as f:
                style = f.read()
            self.setStyleSheet(style)
        except Exception as e:
            print("Erro ao carregar stylesheet:", e)

    # ------------------------------------------------------------------
    # Carregar grafo
    # ------------------------------------------------------------------

    def on_load_graph(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selecione o arquivo de grafo", "", "Text files (*.txt)"
        )
        if not filepath:
            return

        try:
            n, adj = load_graph(filepath)
            self.logger.log(f"Grafo carregado: {filepath}", "SUCCESS")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
            self.logger.log(f"Erro ao carregar grafo: {e}", "ERROR")
            return

        edges = [(u, v) for u in range(n) for v in adj[u] if u < v]

        self.current_n = n
        self.current_edges = edges

        self.graph_canvas.draw_graph(n, edges)
        self.label_status.setText(f"Grafo carregado: {n} vértices.")
        self.logger.log(f"Grafo com {n} vértices e {len(edges)} arestas.", "INFO")

    # ------------------------------------------------------------------
    # Gerar grafo aleatório
    # ------------------------------------------------------------------

    # ============================================================
    #  ABA EXPERIMENTOS (INTEIRA E INDEPENDENTE)
    # ============================================================
    def build_experiments_tab(self):
        from PyQt6.QtWidgets import (
            QWidget, QVBoxLayout, QLabel, QComboBox,
            QSpinBox, QPushButton, QTextEdit
        )

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Tamanho
        layout.addWidget(QLabel("Tamanho do grafo (n):"))
        self.exp_size = QSpinBox()
        self.exp_size.setRange(5, 100)
        self.exp_size.setValue(20)
        layout.addWidget(self.exp_size)

        # Densidade
        layout.addWidget(QLabel("Densidade do grafo:"))
        self.exp_density = QComboBox()
        self.exp_density.addItems(["sparse", "medium", "dense"])
        layout.addWidget(self.exp_density)

        # Repetições
        layout.addWidget(QLabel("Repetições:"))
        self.exp_reps = QSpinBox()
        self.exp_reps.setRange(1, 100)
        self.exp_reps.setValue(5)
        layout.addWidget(self.exp_reps)

        # Botão executar
        self.btn_exp_run = QPushButton("Executar Experimentos")
        self.btn_exp_run.clicked.connect(self.on_run_experiments)
        layout.addWidget(self.btn_exp_run)

        # Botão exportar CSV
        self.btn_exp_export = QPushButton("Exportar CSV")
        self.btn_exp_export.clicked.connect(self.on_export_csv)
        layout.addWidget(self.btn_exp_export)

        # Caixa de logs local da aba
        self.exp_output = QTextEdit()
        self.exp_output.setReadOnly(True)
        self.exp_output.setMinimumHeight(300)
        layout.addWidget(self.exp_output)

        return tab

    def on_run_experiments(self):
        """
        Roda experimentos usando o módulo externo experiments/
        sem tocar na lógica atual da GUI.
        """
        

        n = self.exp_size.value()
        density = self.exp_density.currentText()
        reps = self.exp_reps.value()

        self.exp_output.append(f"\n--- Executando experimentos ---")
        self.exp_output.append(f"n={n}, densidade={density}, repetições={reps}\n")

        results = run_experiments(n, density, reps)
        self.experiment_last = results

        bt_times = [r["bt_time"] for r in results["runs"]]
        h_times = [r["h_time"] for r in results["runs"]]
        bt_success = sum(r["bt_success"] for r in results["runs"])
        h_success = sum(r["h_success"] for r in results["runs"])

        self.exp_output.append("Backtracking:")
        self.exp_output.append(f"  Tempo médio: {sum(bt_times)/len(bt_times):.5f}s")
        self.exp_output.append(f"  Sucesso: {bt_success}/{reps}")

        self.exp_output.append("\nHeurística:")
        self.exp_output.append(f"  Tempo médio: {sum(h_times)/len(h_times):.5f}s")
        self.exp_output.append(f"  Sucesso: {h_success}/{reps}")

        self.exp_output.append("\n--- Concluído ---\n")



    def on_generate_graph(self):
        n = self.spin_n.value()
        text = self.combo_density.currentText()

        p = 0.2 if "0.2" in text else (0.8 if "0.8" in text else 0.5)

        edges = generate_random_graph(n, p)
        self.current_n = n
        self.current_edges = edges

        self.graph_canvas.draw_graph(n, edges)
        self.label_status.setText(f"Grafo gerado: n={n}, p={p}")
        self.logger.log(f"Grafo aleatório gerado (n={n}, p={p}).", "SUCCESS")

    # ------------------------------------------------------------------
    # Comparação exato vs heurística
    # ------------------------------------------------------------------

    def on_compare(self):
        if self.current_n == 0:
            self.logger.log("Nenhum grafo para comparar.", "WARNING")
            return

        window = ComparisonWindow(self.current_n, self.current_edges, parent=self)
        window.show()
        self.logger.log("Janela de comparação aberta.", "INFO")

    # ------------------------------------------------------------------
    # Animação do backtracking
    # ------------------------------------------------------------------

    def on_start_animation(self):
        if self.current_n == 0:
            self.logger.log("Tentativa de animar sem grafo.", "WARNING")
            return

        n, adj = self._build_adj_list()
        self.step_generator = hamiltonian_path_backtracking_steps(n, adj)

        self.graph_canvas.draw_graph(self.current_n, self.current_edges)
        self.animation_timer.start()

        self.logger.log("Animação do backtracking iniciada.", "INFO")

    def on_animation_step(self):
        if self.step_generator is None:
            return

        try:
            state, path = next(self.step_generator)
        except StopIteration:
            self.animation_timer.stop()
            self.logger.log("Animação concluída.", "SUCCESS")
            return

        if state == "visit":
            self.logger.log(f"visit → {path[-1]}", "DEBUG")
        elif state == "backtrack":
            self.logger.log(f"backtrack → {path}", "WARNING")
        elif state == "solution":
            self.label_status.setText(f"Solução encontrada: {path}")
            self.logger.log(f"SOLUÇÃO ENCONTRADA → {path}", "SUCCESS")

            # Mostrar caminho final
            self.graph_canvas.draw_graph(self.current_n, self.current_edges, path)

            # PARAR tudo imediatamente
            self.animation_timer.stop()
            self.step_generator = None

            return

        elif state == "fail":
            self.logger.log("Nenhum caminho Hamiltoniano.", "ERROR")

        self.graph_canvas.draw_graph(self.current_n, self.current_edges, path)

    # ------------------------------------------------------------------
    # Execução exata
    # ------------------------------------------------------------------

    def on_run_exact(self):
        if self.current_n == 0:
            self.logger.log("Executar exato sem grafo.", "WARNING")
            return

        n, adj = self._build_adj_list()

        self.logger.log("Executando backtracking exato...", "INFO")
        t0 = time.time()
        path = hamiltonian_path_backtracking(n, adj)
        t1 = time.time()

        self.label_exact_time.setText(f"{t1 - t0:.4f}s")

        if path:
            self.logger.log(f"Caminho encontrado: {path}", "SUCCESS")
            self.graph_canvas.draw_graph(self.current_n, self.current_edges, path)
        else:
            self.logger.log("Nenhum caminho encontrado (exato).", "ERROR")
            self.graph_canvas.draw_graph(self.current_n, self.current_edges, None)

    # ------------------------------------------------------------------
    # Execução heurística
    # ------------------------------------------------------------------

    def on_run_heur(self):
        if self.current_n == 0:
            self.logger.log("Executar heurística sem grafo.", "WARNING")
            return

        n, adj = self._build_adj_list()

        self.logger.log("Executando heurística...", "INFO")
        t0 = time.time()
        path = heuristic_hamiltonian_path(n, adj)
        t1 = time.time()

        self.label_heur_time.setText(f"{t1 - t0:.4f}s")

        if path:
            self.logger.log(f"Caminho heurístico: {path}", "SUCCESS")
            self.graph_canvas.draw_graph(self.current_n, self.current_edges, path)
        else:
            self.logger.log("Heurística falhou em encontrar caminho.", "ERROR")
            self.graph_canvas.draw_graph(self.current_n, self.current_edges, None)

    # ------------------------------------------------------------------
    # Utilitário para construir adjacência
    # ------------------------------------------------------------------

    def _build_adj_list(self):
        adj = [[] for _ in range(self.current_n)]
        for u, v in self.current_edges:
            adj[u].append(v)
            adj[v].append(u)
        return self.current_n, adj


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
