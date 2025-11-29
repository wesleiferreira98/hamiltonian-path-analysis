# gui/graph_canvas.py
"""
from typing import List, Optional, Iterable, Tuple
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolTip
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QPoint
import networkx as nx
import math


class GraphCanvas(QWidget):
    
    #Widget interativo com:
    #- clique para destacar vértice
    #- clique + arrastar vértice com blitting (ultra rápido)
    #- caminhos Hamiltonianos
    

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tooltip = None
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.n = 0
        self.edges: List[Tuple[int, int]] = []
        self.current_path: Optional[List[int]] = None

        self._pos_cache = None
        self.highlighted_nodes = set()
        self.dragging_node = None

        # coleções que serão atualizadas
        self._node_collection = None
        self._edge_collection = None
        self._path_collection = None

        # background usado no blitting
        self._background = None

        # registro dos eventos
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

        self.figure.patch.set_facecolor("#1e1e1e")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(labelcolor="#cccccc")



    # ============================================================
    # DESENHO COMPLETO
    # ============================================================
    def draw_graph(
        self,
        n: int,
        edges: Iterable[Tuple[int, int]],
        hamiltonian_path: Optional[List[int]] = None,
    ):

        self.n = n
        self.edges = list(edges)
        self.current_path = hamiltonian_path

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_axis_off()

        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)

        if self._pos_cache is None or len(self._pos_cache) != n:
            self._pos_cache = nx.spring_layout(G, seed=42)

        pos = self._pos_cache

        # --------------------------
        # desenhar nós
        # --------------------------
        self._node_collection = nx.draw_networkx_nodes(
            G, pos, ax=ax,
            node_color=[
                "tab:orange" if v in self.highlighted_nodes else "lightgray"
                for v in G.nodes()
            ],
            node_size=[
                700 if v in self.highlighted_nodes else 500
                for v in G.nodes()
            ],
            edgecolors=[
                "black" if v in self.highlighted_nodes else "none"
                for v in G.nodes()
            ],
            linewidths=2
        )

        # --------------------------
        # desenhar arestas gerais
        # --------------------------
        self._edge_collection = nx.draw_networkx_edges(
            G, pos, ax=ax, alpha=0.4
        )

        # --------------------------
        # desenhar caminho Hamiltoniano
        # --------------------------
        self._path_collection = None
        if hamiltonian_path and len(hamiltonian_path) > 1:
            path_edges = list(zip(hamiltonian_path, hamiltonian_path[1:]))

            self._path_collection = nx.draw_networkx_edges(
                G, pos,
                edgelist=path_edges,
                ax=ax,
                width=3,
                edge_color="tab:red",
            )

        # labels (não serão redesenhados no arrasto!)
        nx.draw_networkx_labels(G, pos, ax=ax)

        self.canvas.draw()

        # salvar fundo (para blitting)
        self._background = self.canvas.copy_from_bbox(ax.bbox)
    
    
    def mpl_to_qt(self, event):
        #Converte coordenadas Matplotlib → Qt Global com precisão.
        # Caso Matplotlib tenha um evento Qt válido
        if hasattr(event, "guiEvent") and event.guiEvent is not None:
            qt_event = event.guiEvent

            # posição local dentro do widget Qt
            pos = qt_event.position()  # QPointF

            # converter para inteiro e para global
            local_point = QPoint(int(pos.x()), int(pos.y()))
            return self.canvas.mapToGlobal(local_point)

        # fallback (caso raro)
        return self.canvas.mapToGlobal(QPoint(int(event.x), int(event.y)))



    def on_hover(self, event):
        if event.inaxes is None:
            QToolTip.hideText()
            return

        node = self._detect_node(event.xdata, event.ydata)
        if node is None:
            QToolTip.hideText()
            return

        # Descobrir vizinhos
        neighbors = sorted(
            [v for (u, v) in self.edges if u == node] +
            [u for (u, v) in self.edges if v == node]
        )
        degree = len(neighbors)

        info = f"Vértice: {node}\nGrau: {degree}\nVizinhos: {neighbors}"

        if self.current_path and node in self.current_path:
            idx = self.current_path.index(node)
            info += f"\nPosição no caminho: {idx}"

        # Mostrar tooltip Qt no lugar correto
        global_pos = self.mpl_to_qt(event)
        QToolTip.showText(global_pos, info, self)



    # ============================================================
    # EVENTO: CLIQUE
    # ============================================================
    def on_click(self, event):
        if event.inaxes is None:
            return

        node = self._detect_node(event.xdata, event.ydata)
        if node is None:
            return

        # toggle de destaque
        if node in self.highlighted_nodes:
            self.highlighted_nodes.remove(node)
        else:
            self.highlighted_nodes.add(node)

        # inicia arrasto
        self.dragging_node = node

        # redesenho completo da figura
        self.draw_graph(self.n, self.edges, self.current_path)

    # ============================================================
    # EVENTO: ARRASTAR (rápido com blitting)
    # ============================================================
    def on_drag(self, event):
        global_pos = self.mpl_to_qt(event)
        node = self.dragging_node

        if node is not None:
            neighbors = sorted(
                [v for (u, v) in self.edges if u == node] +
                [u for (u, v) in self.edges if v == node]
            )
            degree = len(neighbors)

            info = f"Vértice: {node}\nGrau: {degree}\nVizinhos: {neighbors}"

            if self.current_path and node in self.current_path:
                idx = self.current_path.index(node)
                info += f"\nPosição no caminho: {idx}"

            QToolTip.showText(global_pos, info, self)

        if self.dragging_node is None or event.inaxes is None:
            return

        # Desativa tooltip durante arrasto
        if self.tooltip:
            self.tooltip.set_visible(False)

        # atualiza a posição do nó arrastado
        self._pos_cache[self.dragging_node] = (event.xdata, event.ydata)

        ax = self.figure.axes[0]

        # restaura BACKGROUND (ultra rápido)
        self.canvas.restore_region(self._background)

        # -----------------------------------
        # atualizar nós
        # -----------------------------------
        new_pos = [self._pos_cache[i] for i in range(self.n)]
        self._node_collection.set_offsets(new_pos)

        # -----------------------------------
        # atualizar arestas
        # -----------------------------------
        segments = [
            [self._pos_cache[u], self._pos_cache[v]]
            for u, v in self.edges
        ]
        self._edge_collection.set_segments(segments)

        # -----------------------------------
        # atualizar caminho Hamiltoniano (se existir)
        # -----------------------------------
        if self._path_collection and self.current_path:
            path_segments = [
                [self._pos_cache[a], self._pos_cache[b]]
                for a, b in zip(self.current_path, self.current_path[1:])
            ]
            self._path_collection.set_segments(path_segments)

        # -----------------------------------
        # desenha partes móveis
        # -----------------------------------
        ax.draw_artist(self._node_collection)
        ax.draw_artist(self._edge_collection)
        if self._path_collection:
            ax.draw_artist(self._path_collection)
        
        # blit → atualiza só o bbox
        self.canvas.blit(ax.bbox)
       

    # ============================================================
    # EVENTO: SOLTAR
    # ============================================================
    def on_release(self, event):
        self.dragging_node = None

        # recapturar background com nova posição
        ax = self.figure.axes[0]
        self.canvas.draw()
        self._background = self.canvas.copy_from_bbox(ax.bbox)


    # ============================================================
    # DETECTAR NÓ
    # ============================================================
    def _detect_node(self, x, y):
        if self._pos_cache is None:
            return None

        threshold = 0.05
        for node, (nx_x, nx_y) in self._pos_cache.items():
            if math.dist([x, y], [nx_x, nx_y]) < threshold:
                return node
        return None

"""

# ESTILIZAÇÃO APLICADA: VSCode Dark+
# Nenhuma funcionalidade alterada

import math
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolTip
from PyQt6.QtCore import QPoint
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx


class GraphCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Tema VSCode Dark+ com eixos visíveis
        self.figure.patch.set_facecolor("#1e1e1e")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(labelcolor="#cccccc", colors="#cccccc")

        for spine in self.ax.spines.values():
            spine.set_color("#cccccc")
            spine.set_visible(True)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Estados
        self.n = 0
        self.edges: List[Tuple[int, int]] = []
        self.current_path: Optional[List[int]] = None
        self.highlighted_nodes = set()
        self.dragging_node = None
        self._pos_cache = None

        # Blitting
        self._node_collection = None
        self._edge_collection = None
        self._path_collection = None
        self._background = None

        # Eventos
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    # ======================================================================
    # DESENHO DO GRAFO (COM GLOW, GRID, EIXOS)
    # ======================================================================

    def draw_graph(self, n: int, edges: List[Tuple[int, int]], path: Optional[List[int]] = None):
        self.n = n
        self.edges = edges
        self.current_path = path

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Fundo + eixos
        ax.set_facecolor("#1e1e1e")

        # EIXOS SEMPRE VISÍVEIS
        ax.tick_params(labelcolor="#cccccc", colors="#cccccc")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#cccccc")

        # Limites fixos
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)

        # GRID PONTILHADO
        ax.grid(
            True,
            linestyle=":",
            linewidth=0.7,
            alpha=0.35,
            color="#555555"
        )

        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(edges)

        if self._pos_cache is None or len(self._pos_cache) != n:
            self._pos_cache = nx.spring_layout(G, seed=42)

        pos = self._pos_cache

        # ============================================================
        # ARESTAS BRANCAS
        # ============================================================

        self._edge_collection = nx.draw_networkx_edges(
            G, pos, ax=ax,
            width=1.5,
            alpha=0.85,
            edge_color="#FFFFFF"
        )

        # ============================================================
        # CAMINHO (AZUL)
        # ============================================================

        self._path_collection = None
        if path and len(path) > 1:
            path_edges = list(zip(path, path[1:]))

            self._path_collection = nx.draw_networkx_edges(
                G, pos,
                ax=ax,
                edgelist=path_edges,
                width=3.5,
                edge_color="#0e639c"
            )

        # ============================================================
        # GLOW
        # ============================================================

        glow_positions = [pos[v] for v in G.nodes()]
        glow_sizes = [1500 if v in self.highlighted_nodes else 900 for v in G.nodes()]

        ax.scatter(
            [p[0] for p in glow_positions],
            [p[1] for p in glow_positions],
            s=glow_sizes,
            c="#4fc3f7",
            alpha=0.12,
            linewidths=0,
        )

        # ============================================================
        # NÓS
        # ============================================================

        self._node_collection = nx.draw_networkx_nodes(
            G, pos, ax=ax,
            node_color=[
                "#1e90ff" if v in self.highlighted_nodes else "#4fc3f7"
                for v in G.nodes()
            ],
            edgecolors=[
                "#0e639c" if v in self.highlighted_nodes else "#1e1e1e"
                for v in G.nodes()
            ],
            linewidths=2,
            node_size=[
                750 if v in self.highlighted_nodes else 550
                for v in G.nodes()
            ]
        )

        # ============================================================
        # LABELS
        # ============================================================

        nx.draw_networkx_labels(
            G, pos, ax=ax,
            font_color="#000000",
            font_size=10
        )

        self.canvas.draw()
        self._background = self.canvas.copy_from_bbox(ax.bbox)

    # ======================================================================
    # Tooltip / hover
    # ======================================================================

    def mpl_to_qt(self, event):
        if hasattr(event, "guiEvent") and event.guiEvent is not None:
            qt_event = event.guiEvent
            pos = qt_event.position()
            return self.canvas.mapToGlobal(QPoint(int(pos.x()), int(pos.y())))
        return self.canvas.mapToGlobal(QPoint(int(event.x), int(event.y)))

    def on_hover(self, event):
        if event.inaxes is None:
            QToolTip.hideText()
            return

        node = self._detect_node(event.xdata, event.ydata)
        if node is None:
            QToolTip.hideText()
            return

        neighbors = sorted(
            [v for (u, v) in self.edges if u == node] +
            [u for (u, v) in self.edges if v == node]
        )
        degree = len(neighbors)

        info = f"Vértice: {node}\nGrau: {degree}\nVizinhos: {neighbors}"
        if self.current_path and node in self.current_path:
            idx = self.current_path.index(node)
            info += f"\nPosição no caminho: {idx}"

        global_pos = self.mpl_to_qt(event)
        QToolTip.showText(global_pos, info, self)

    # ======================================================================
    # Clique
    # ======================================================================

    def on_click(self, event):
        if event.inaxes is None:
            return

        node = self._detect_node(event.xdata, event.ydata)
        if node is None:
            return

        if node in self.highlighted_nodes:
            self.highlighted_nodes.remove(node)
        else:
            self.highlighted_nodes.add(node)

        self.dragging_node = node
        self.draw_graph(self.n, self.edges, self.current_path)

    # ======================================================================
    # Arrasto (blitting)
    # ======================================================================

    def on_drag(self, event):
        if self.dragging_node is None:
            return
        if event.inaxes is None or event.xdata is None:
            return

        self._pos_cache[self.dragging_node] = (event.xdata, event.ydata)

        ax = self.figure.axes[0]
        self.canvas.restore_region(self._background)

        # atualizar nós
        new_pos = [self._pos_cache[i] for i in range(self.n)]
        self._node_collection.set_offsets(new_pos)

        # atualizar arestas
        segments = [[self._pos_cache[u], self._pos_cache[v]] for u, v in self.edges]
        self._edge_collection.set_segments(segments)

        # atualizar caminho
        if self.current_path and self._path_collection:
            pseg = [[self._pos_cache[a], self._pos_cache[b]] for a, b in zip(self.current_path, self.current_path[1:])]
            self._path_collection.set_segments(pseg)

        ax.draw_artist(self._node_collection)
        ax.draw_artist(self._edge_collection)
        if self._path_collection:
            ax.draw_artist(self._path_collection)

        self.canvas.blit(ax.bbox)

    # ======================================================================
    # Soltar nó
    # ======================================================================

    def on_release(self, event):
        self.dragging_node = None
        ax = self.figure.axes[0]
        self.canvas.draw()
        self._background = self.canvas.copy_from_bbox(ax.bbox)

    # ======================================================================
    # Detectar nó
    # ======================================================================

    def _detect_node(self, x, y):
        if self._pos_cache is None:
            return None

        threshold = 0.05
        for node, (nx_x, nx_y) in self._pos_cache.items():
            if math.dist([x, y], [nx_x, nx_y]) < threshold:
                return node
        return None

