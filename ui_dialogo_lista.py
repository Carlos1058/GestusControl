# ui_dialogo_lista.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea,
    QWidget, QDialogButtonBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor
from estilos import HOJA_ESTILO


class DialogoListaGestos(QDialog):
    def __init__(self, gestos, acciones, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lista Completa de Gestos")
        self.setMinimumSize(520, 620)
        self.setStyleSheet(HOJA_ESTILO)

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
        titulo.setObjectName("Titulo")
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

            label_titulo = QLabel(f"<b>{gesto.get('emoji', '')} {gesto['nombre'].replace('_', ' ').title()}</b>")
            label_titulo.setObjectName("InfoTexto")
            # Estilo específico para el título de la tarjeta si es necesario, o confiar en InfoTexto
            label_titulo.setStyleSheet("font-size: 18px; color: #00E5FF;") 

            label_accion = QLabel(f"Acción: <i>{acciones[gesto['accion']]['nombre']}</i>")
            label_accion.setObjectName("InfoTexto")
            
            label_desc = QLabel(f"{acciones[gesto['accion']]['descripcion']}")
            label_desc.setObjectName("InfoTexto")
            label_desc.setWordWrap(True)

            tarjeta_layout.addWidget(label_titulo)
            tarjeta_layout.addWidget(label_accion)
            tarjeta_layout.addWidget(label_desc)

            layout_gestos.addWidget(tarjeta)

        layout_gestos.addStretch(1)

        # --- Botón OK ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
