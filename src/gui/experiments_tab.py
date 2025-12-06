# src/gui/experiments_tab.py
"""
Aba de experimentos com visualização de grafos integrada.
Permite configurar e executar experimentos sistemáticos.
"""

import sys
import os
from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QPushButton, QTextEdit,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QSplitter, QTabWidget, QFileDialog, QProgressBar,
    QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import time

# Adicionar o diretório raiz ao path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.gui.graph_canvas import GraphCanvas
from src.experiments.experiment_runner import ExperimentRunner


class ExperimentWorker(QThread):
    """Worker thread para executar experimentos sem travar a GUI."""
    
    progress = pyqtSignal(str)  # mensagem de progresso
    finished = pyqtSignal(dict)  # resultado final
    error = pyqtSignal(str)  # erro
    
    def __init__(self, runner: ExperimentRunner, n: int, density: str, reps: int):
        super().__init__()
        self.runner = runner
        self.n = n
        self.density = density
        self.reps = reps
    
    def run(self):
        """Executa experimento em thread separada."""
        try:
            self.progress.emit(f"Iniciando experimento: n={self.n}, densidade={self.density}, repetições={self.reps}")
            result = self.runner.run_single_experiment(self.n, self.density, self.reps)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class BatchExperimentWorker(QThread):
    """Worker para batch de experimentos."""
    
    progress = pyqtSignal(str, int, int)  # mensagem, atual, total
    finished = pyqtSignal(list)  # resultados
    error = pyqtSignal(str)
    
    def __init__(self, runner: ExperimentRunner, sizes: List[int], densities: List[str], reps: int):
        super().__init__()
        self.runner = runner
        self.sizes = sizes
        self.densities = densities
        self.reps = reps
    
    def run(self):
        """Executa batch de experimentos."""
        try:
            total = len(self.sizes) * len(self.densities)
            current = 0
            
            for n in self.sizes:
                for density in self.densities:
                    current += 1
                    self.progress.emit(
                        f"Executando: n={n}, densidade={density}",
                        current,
                        total
                    )
                    self.runner.run_single_experiment(n, density, self.reps)
            
            self.finished.emit(self.runner.results)
        except Exception as e:
            self.error.emit(str(e))


class ExperimentsTab(QWidget):
    """Aba completa de experimentos com visualização integrada."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estado
        self.experiment_runner = ExperimentRunner()
        self.current_result: Optional[Dict] = None
        self.current_graph_n = 0
        self.current_graph_edges = []
        self.worker: Optional[QThread] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura interface da aba."""
        main_layout = QHBoxLayout(self)
        
        # Splitter principal: controles | visualização
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === PAINEL ESQUERDO: Controles ===
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)
        
        # === PAINEL DIREITO: Visualização ===
        right_panel = self._create_visualization_panel()
        splitter.addWidget(right_panel)
        
        # Proporção 1:2 (controles menor que visualização)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
    
    def _create_control_panel(self) -> QWidget:
        """Cria painel de controles."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # === EXPERIMENTO INDIVIDUAL ===
        group_single = QGroupBox("Experimento Individual")
        single_layout = QVBoxLayout()
        
        # Tamanho
        h_size = QHBoxLayout()
        h_size.addWidget(QLabel("Tamanho (n):"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(5, 100)
        self.spin_n.setValue(10)
        h_size.addWidget(self.spin_n)
        single_layout.addLayout(h_size)
        
        # Densidade
        h_density = QHBoxLayout()
        h_density.addWidget(QLabel("Densidade:"))
        self.combo_density = QComboBox()
        self.combo_density.addItems(["sparse", "medium", "dense"])
        h_density.addWidget(self.combo_density)
        single_layout.addLayout(h_density)
        
        # Repetições
        h_reps = QHBoxLayout()
        h_reps.addWidget(QLabel("Repetições:"))
        self.spin_reps = QSpinBox()
        self.spin_reps.setRange(1, 100)
        self.spin_reps.setValue(5)
        h_reps.addWidget(self.spin_reps)
        single_layout.addLayout(h_reps)
        
        # Botão executar
        self.btn_run_single = QPushButton("Executar Experimento")
        self.btn_run_single.clicked.connect(self.on_run_single_experiment)
        single_layout.addWidget(self.btn_run_single)
        
        group_single.setLayout(single_layout)
        layout.addWidget(group_single)
        
        # === BATCH DE EXPERIMENTOS ===
        group_batch = QGroupBox("Batch de Experimentos")
        batch_layout = QVBoxLayout()
        
        batch_layout.addWidget(QLabel("Tamanhos: 10, 20, 30, 40, 50"))
        batch_layout.addWidget(QLabel("Densidades: sparse, medium, dense"))
        
        h_batch_reps = QHBoxLayout()
        h_batch_reps.addWidget(QLabel("Repetições:"))
        self.spin_batch_reps = QSpinBox()
        self.spin_batch_reps.setRange(1, 50)
        self.spin_batch_reps.setValue(5)
        h_batch_reps.addWidget(self.spin_batch_reps)
        batch_layout.addLayout(h_batch_reps)
        
        self.btn_run_batch = QPushButton("Executar Batch")
        self.btn_run_batch.clicked.connect(self.on_run_batch)
        batch_layout.addWidget(self.btn_run_batch)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        batch_layout.addWidget(self.progress_bar)
        
        group_batch.setLayout(batch_layout)
        layout.addWidget(group_batch)
        
        # === EXPORTAR ===
        group_export = QGroupBox("Exportar Resultados")
        export_layout = QVBoxLayout()
        
        self.btn_export_csv = QPushButton("Exportar CSV")
        self.btn_export_csv.clicked.connect(self.on_export_csv)
        self.btn_export_csv.setEnabled(False)
        export_layout.addWidget(self.btn_export_csv)
        
        self.btn_clear = QPushButton("Limpar Resultados")
        self.btn_clear.clicked.connect(self.on_clear_results)
        export_layout.addWidget(self.btn_clear)
        
        group_export.setLayout(export_layout)
        layout.addWidget(group_export)
        
        # Logs
        layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        layout.addWidget(self.log_output)
        
        layout.addStretch()
        
        return panel
    
    def _create_visualization_panel(self) -> QWidget:
        """Cria painel de visualização."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tabs para diferentes visualizações
        tabs = QTabWidget()
        
        # === ABA 1: Grafo ===
        self.graph_canvas = GraphCanvas()
        tabs.addTab(self.graph_canvas, "Visualização do Grafo")
        
        # === ABA 2: Tabela de Resultados ===
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            'n', 'Densidade', 'BT Tempo (s)', 'BT Taxa', 'BT Passos',
            'H Tempo (s)', 'H Taxa', 'Arestas'
        ])
        table_layout.addWidget(self.results_table)
        
        tabs.addTab(table_widget, "Tabela de Resultados")
        
        # === ABA 3: Sumário Textual ===
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFontFamily("Courier New")
        summary_layout.addWidget(self.summary_text)
        
        tabs.addTab(summary_widget, "Sumário")
        
        layout.addWidget(tabs)
        
        return panel
    
    # ================================================================
    # EXECUÇÃO DE EXPERIMENTOS
    # ================================================================
    
    def on_run_single_experiment(self):
        """Executa experimento individual."""
        n = self.spin_n.value()
        density = self.combo_density.currentText()
        reps = self.spin_reps.value()
        
        self.log(f"Iniciando experimento: n={n}, densidade={density}, reps={reps}")
        self.btn_run_single.setEnabled(False)
        
        # Criar worker
        self.worker = ExperimentWorker(self.experiment_runner, n, density, reps)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_experiment_finished)
        self.worker.error.connect(self.on_experiment_error)
        self.worker.start()
    
    def on_run_batch(self):
        """Executa batch de experimentos."""
        sizes = [10, 20, 30, 40, 50]
        densities = ['sparse', 'medium', 'dense']
        reps = self.spin_batch_reps.value()
        
        self.log(f"Iniciando batch: tamanhos={sizes}, densidades={densities}, reps={reps}")
        self.btn_run_batch.setEnabled(False)
        self.btn_run_single.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(sizes) * len(densities))
        
        # Criar worker
        self.worker = BatchExperimentWorker(self.experiment_runner, sizes, densities, reps)
        self.worker.progress.connect(self.on_batch_progress)
        self.worker.finished.connect(self.on_batch_finished)
        self.worker.error.connect(self.on_experiment_error)
        self.worker.start()
    
    def on_experiment_finished(self, result: Dict):
        """Callback quando experimento individual termina."""
        self.current_result = result
        self.log("Experimento concluído!")
        self.btn_run_single.setEnabled(True)
        
        # Atualizar visualizações
        self._update_results_display()
        self.btn_export_csv.setEnabled(True)
        
        # Mostrar último grafo gerado
        if result['runs']:
            last_run = result['runs'][-1]
            # Reconstruir grafo do último run (precisamos gerar novamente ou armazenar)
            # Por simplicidade, vamos apenas logar
            self.log(f"Último run: {last_run['num_edges']} arestas")
    
    def on_batch_progress(self, message: str, current: int, total: int):
        """Atualiza progresso do batch."""
        self.log(message)
        self.progress_bar.setValue(current)
    
    def on_batch_finished(self, results: List[Dict]):
        """Callback quando batch termina."""
        self.log(f"Batch concluído! {len(results)} experimentos executados.")
        self.btn_run_batch.setEnabled(True)
        self.btn_run_single.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Atualizar visualizações
        self._update_results_display()
        self.btn_export_csv.setEnabled(True)
    
    def on_experiment_error(self, error_msg: str):
        """Callback para erros."""
        self.log(f"ERRO: {error_msg}")
        self.btn_run_single.setEnabled(True)
        self.btn_run_batch.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Erro", f"Erro durante experimento:\n{error_msg}")
    
    # ================================================================
    # ATUALIZAÇÃO DE VISUALIZAÇÕES
    # ================================================================
    
    def _update_results_display(self):
        """Atualiza todas as visualizações com resultados."""
        if not self.experiment_runner.results:
            return
        
        # Atualizar tabela
        self._update_results_table()
        
        # Atualizar sumário
        summary = self.experiment_runner.get_summary_table()
        self.summary_text.setPlainText(summary)
    
    def _update_results_table(self):
        """Preenche tabela de resultados."""
        results = self.experiment_runner.results
        self.results_table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            stats = result['statistics']
            
            self.results_table.setItem(i, 0, QTableWidgetItem(str(result['n'])))
            self.results_table.setItem(i, 1, QTableWidgetItem(result['density']))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{stats['bt_avg_time']:.6f}"))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{stats['bt_success_rate']:.2%}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(f"{stats['bt_avg_steps']:.1f}"))
            self.results_table.setItem(i, 5, QTableWidgetItem(f"{stats['h_avg_time']:.6f}"))
            self.results_table.setItem(i, 6, QTableWidgetItem(f"{stats['h_success_rate']:.2%}"))
            
            # Número médio de arestas
            avg_edges = sum(r['num_edges'] for r in result['runs']) / len(result['runs'])
            self.results_table.setItem(i, 7, QTableWidgetItem(f"{avg_edges:.1f}"))
        
        self.results_table.resizeColumnsToContents()
    
    # ================================================================
    # EXPORTAÇÃO E UTILIDADES
    # ================================================================
    
    def on_export_csv(self):
        """Exporta resultados para CSV."""
        if not self.experiment_runner.results:
            QMessageBox.warning(self, "Aviso", "Nenhum resultado para exportar.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar resultados",
            "experiment_results.csv",
            "CSV Files (*.csv)"
        )
        
        if filepath:
            try:
                self.experiment_runner.export_to_csv(filepath)
                self.log(f"Resultados exportados para: {filepath}")
                QMessageBox.information(self, "Sucesso", f"Resultados exportados para:\n{filepath}")
            except Exception as e:
                self.log(f"Erro ao exportar: {e}")
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{e}")
    
    def on_clear_results(self):
        """Limpa todos os resultados."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja limpar todos os resultados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.experiment_runner.results.clear()
            self.results_table.setRowCount(0)
            self.summary_text.clear()
            self.log_output.clear()
            self.btn_export_csv.setEnabled(False)
            self.log("Resultados limpos.")
    
    def log(self, message: str):
        """Adiciona mensagem ao log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
