# gui/comparison_window.py

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt
import time

from src.gui.graph_canvas import GraphCanvas
from src.backtracking import hamiltonian_path_backtracking
from src.heuristic import heuristic_hamiltonian_path


class ComparisonWindow(QWidget):
    """
    Exibe lado a lado o caminho encontrado pelos algoritmos:
    - Backtracking (exato)
    - Heurística
    """

    def __init__(self, n, edges, parent=None):
        super().__init__(parent)

        self.n = n
        self.edges = edges

        self.setWindowTitle("Comparação lado a lado")
        self.resize(1200, 600)

        # Dois canvases
        self.canvas_exact = GraphCanvas(self)
        self.canvas_heur = GraphCanvas(self)

        # Texto de status
        self.label_exact = QLabel("Exato: aguardando execução.")
        self.label_heur = QLabel("Heurística: aguardando execução.")

        # Botão de executar
        btn_run = QPushButton("Executar Comparação")
        btn_run.clicked.connect(self.run_comparison)

        # Layout superior (dois gráficos lado a lado)
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.canvas_exact)
        graph_layout.addWidget(self.canvas_heur)

        # Layout inferior (status + botão)
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.label_exact)
        bottom_layout.addWidget(self.label_heur)
        bottom_layout.addWidget(btn_run)

        layout = QVBoxLayout()
        layout.addLayout(graph_layout)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        # Desenha o grafo inicial sem caminhos
        self.canvas_exact.draw_graph(n, edges)
        self.canvas_heur.draw_graph(n, edges)

    def run_comparison(self):
        # ---------------------------
        # Execução do exact (BACKTRACKING)
        # ---------------------------
        t0 = time.time()
        path_exact = hamiltonian_path_backtracking(self.n, self._make_adj())
        t1 = time.time()

        if path_exact:
            self.label_exact.setText(
                f"Exato: caminho encontrado ({t1 - t0:.4f}s)"
            )
            self.canvas_exact.draw_graph(self.n, self.edges, path_exact)
        else:
            self.label_exact.setText(
                f"Exato: NÃO encontrou caminho ({t1 - t0:.4f}s)"
            )
            self.canvas_exact.draw_graph(self.n, self.edges)

        # ---------------------------
        # Execução da HEURÍSTICA
        # ---------------------------
        t2 = time.time()
        path_heur = heuristic_hamiltonian_path(self.n, self._make_adj())
        t3 = time.time()

        if path_heur:
            self.label_heur.setText(
                f"Heurística: caminho encontrado ({t3 - t2:.4f}s)"
            )
            self.canvas_heur.draw_graph(self.n, self.edges, path_heur)
        else:
            self.label_heur.setText(
                f"Heurística: NÃO encontrou caminho ({t3 - t2:.4f}s)"
            )
            self.canvas_heur.draw_graph(self.n, self.edges)

    def _make_adj(self):
        adj = [[] for _ in range(self.n)]
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        return adj
