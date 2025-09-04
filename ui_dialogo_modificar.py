# ui_dialogo_modificar.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QComboBox, QDialogButtonBox)
import json

class DialogoModificar(QDialog):
    def __init__(self, config_actual, acciones_disponibles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Asignación de Gestos")
        self.setMinimumSize(450, 220)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel { font-size: 14px; color: #000000; }
            QComboBox {
                font-size: 14px; padding: 5px; color: #000000;
                background-color: #F0F0F0; border: 1px solid #CCCCCC; border-radius: 3px;
            }
            QPushButton {
                background-color: #E1E1E1; color: #000000; font-size: 14px;
                padding: 8px 15px; border-radius: 5px; border: 1px solid #CCCCCC;
            }
            QPushButton:hover { background-color: #D1D1D1; }
        """)

        # Guardamos la configuración y acciones para usarlas en los métodos
        self.config_modificada = config_actual.copy()
        self.acciones_disponibles = acciones_disponibles
        
        # --- Layouts y Widgets ---
        layout = QVBoxLayout(self)
        info_label = QLabel("Seleccione un gesto para cambiar la acción que realiza:")
        layout.addWidget(info_label)

        self.combo_gestos = QComboBox()
        self.combo_acciones = QComboBox()
        layout.addWidget(self.combo_gestos)
        layout.addWidget(self.combo_acciones)
        layout.addStretch(1)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # --- Lógica de la Interfaz ---
        self.cargar_datos_iniciales()
        self.combo_gestos.currentIndexChanged.connect(self.actualizar_combo_acciones)
        self.combo_acciones.currentIndexChanged.connect(self.registrar_cambio_accion)

    def cargar_datos_iniciales(self):
        """Puebla los ComboBox con los datos iniciales del config."""
        # Poblar gestos (excluimos 'LIKE' que es para confirmación)
        gestos_editables = [g for g in self.config_modificada if self.config_modificada[g]['accion'] != 'confirmacion']
        self.combo_gestos.addItems(gestos_editables)
        
        # Poblar acciones
        self.combo_acciones.addItems(self.acciones_disponibles)
        
        # Sincronizar la selección inicial
        self.actualizar_combo_acciones()

    def actualizar_combo_acciones(self):
        """Al cambiar de gesto, muestra la acción que tiene asignada actualmente."""
        gesto_seleccionado = self.combo_gestos.currentText()
        if gesto_seleccionado:
            accion_actual = self.config_modificada[gesto_seleccionado]['accion']
            self.combo_acciones.setCurrentText(accion_actual)

    def registrar_cambio_accion(self):
        """Actualiza el diccionario en memoria cuando el usuario cambia una acción."""
        gesto_seleccionado = self.combo_gestos.currentText()
        accion_seleccionada = self.combo_acciones.currentText()
        if gesto_seleccionado and accion_seleccionada:
            self.config_modificada[gesto_seleccionado]['accion'] = accion_seleccionada
    
    def obtener_config_actualizada(self):
        """Método para que la ventana principal obtenga la configuración final."""
        return self.config_modificada