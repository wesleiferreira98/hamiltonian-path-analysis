# src/gui/logger_widget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog
from PyQt6.QtCore import QDateTime


class LoggerWidget(QWidget):
    """
    Logger avançado com níveis de log, cores, timestamps e exportação.
    """

    COLORS = {
        "INFO": "#00b7ff",
        "SUCCESS": "#00ff66",
        "WARNING": "#ffbb00",
        "ERROR": "#ff4444",
        "DEBUG": "#bbbbbb",
    }

    def __init__(self):
        super().__init__()

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #cccccc;
                font-family: Consolas, monospace;
                font-size: 12px;
                border: 1px solid #333;
            }
        """)

        btn_clear = QPushButton("Limpar Logs")
        btn_clear.clicked.connect(self.clear_logs)

        btn_export = QPushButton("Exportar Logs")
        btn_export.clicked.connect(self.export_logs)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(btn_clear)
        layout.addWidget(btn_export)

        self.setLayout(layout)

    # ------------------------------------------------------------
    # API principal de logging
    # ------------------------------------------------------------
    def log(self, message, level="INFO", timestamp=True):
        color = self.COLORS.get(level, "#cccccc")
        prefix = ""

        if timestamp:
            ts = QDateTime.currentDateTime().toString("hh:mm:ss")
            prefix = f"<b>[{ts}]</b> "

        html = f"{prefix}<span style='color:{color}'>[{level}]</span> {message}"
        self.text.append(html)
        self.text.ensureCursorVisible()

    # ------------------------------------------------------------
    def clear_logs(self):
        self.text.clear()

    # ------------------------------------------------------------
    def export_logs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar logs", "logs.txt", "Text Files (*.txt)"
        )
        if not path:
            return

        content = self.text.toPlainText()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
