# ui_dialogo_lista.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QScrollArea, 
                             QWidget, QDialogButtonBox, QFrame)
import json

class DialogoListaGestos(QDialog):
    def __init__(self, config_gestos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lista Completa de Gestos")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel { font-size: 14px; color: #000000; }
            QScrollArea { border: none; }
        """)

        layout = QVBoxLayout(self)

        # Área de scroll para la lista
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Contenedor para los widgets dentro del scroll
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        layout_gestos = QVBoxLayout(scroll_content)

        # Llenar la lista de gestos
        for nombre_gesto, datos in config_gestos.items():
            # Formatear el texto para que sea legible
            nombre_limpio = nombre_gesto.replace('_', ' ').title()
            accion_limpia = datos['accion'].replace('_', ' ')
            descripcion = datos['descripcion']

            texto_gesto = f"<b>{nombre_limpio}</b> → <i>{accion_limpia}</i>"
            label_gesto = QLabel(texto_gesto)
            label_gesto.setStyleSheet("font-size: 16px;")
            
            label_desc = QLabel(f"     {descripcion}")
            label_desc.setStyleSheet("color: #555555; font-size: 14px; margin-bottom: 10px;")
            
            layout_gestos.addWidget(label_gesto)
            layout_gestos.addWidget(label_desc)
        
        layout_gestos.addStretch(1)

        # Botón de Aceptar
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)