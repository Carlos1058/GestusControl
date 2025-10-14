# ui_dialogo_lista.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea,
    QWidget, QDialogButtonBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor


class DialogoListaGestos(QDialog):
    def __init__(self, gestos, acciones, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lista Completa de Gestos")
        self.setMinimumSize(520, 620)
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
                border-radius: 10px;
            }

            QLabel {
                color: #222222;
                font-family: 'Segoe UI';
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            /* Tarjeta visual */
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
                margin-bottom: 10px;
            }

            /* Botón */
            QPushButton {
                background-color: #4CAF50;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)

        # --- Efecto de sombra general ---
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setOffset(0, 0)
        sombra.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(sombra)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Lista completa de gestos y sus acciones")
        titulo.setStyleSheet("font-size: 17px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titulo)

        # Área de scroll
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        layout_gestos = QVBoxLayout(scroll_content)
        layout_gestos.setSpacing(10)
        layout_gestos.setContentsMargins(5, 5, 5, 5)

        # --- Crea una tarjeta por cada gesto ---
        for gesto in gestos:

            tarjeta = QFrame()
            tarjeta_layout = QVBoxLayout(tarjeta)
            tarjeta_layout.setContentsMargins(12, 10, 12, 10)
            tarjeta_layout.setSpacing(4)

            label_titulo = QLabel(f"<b>{gesto['nombre']}</b>")
            label_titulo.setStyleSheet("font-size: 16px; color: #1B5E20;")

            label_accion = QLabel(f"Acción: <i>{acciones[gesto['accion']]['nombre']}</i>")
            label_accion.setStyleSheet("font-size: 14px; color: #000000;")
            label_desc = QLabel(f"{acciones[gesto['accion']]['descripcion']}")

            label_desc.setWordWrap(True)
            label_desc.setStyleSheet("font-size: 13px; color: #000000;")

            tarjeta_layout.addWidget(label_titulo)
            tarjeta_layout.addWidget(label_accion)
            tarjeta_layout.addWidget(label_desc)

            layout_gestos.addWidget(tarjeta)

        layout_gestos.addStretch(1)

        # --- Botón OK ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
