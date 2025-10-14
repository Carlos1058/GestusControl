# ui_dialogo_modificar.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QComboBox, QDialogButtonBox, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor


class DialogoModificar(QDialog):
    def __init__(self, config_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Asignación de Gestos")
        self.setMinimumSize(460, 230)
        self.setStyleSheet("""
            QDialog { 
                background-color: #FFFFFF;
                border-radius: 10px;
            }

            QLabel {
                font-size: 15px;
                color: #222222;
                font-weight: 500;
                margin-bottom: 6px;
            }

            /* ComboBox */
            QComboBox {
                font-size: 14px;
                padding: 6px 8px;
                color: #202020;
                background-color: #FAFAFA;
                border: 1px solid #CCCCCC;
                border-radius: 6px;
            }
            QComboBox:hover {
                background-color: #FFFFFF;
                border: 1px solid #4CAF50;
            }

            /* Estilo del menú desplegable */
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #BBBBBB;
                border-radius: 4px;
                selection-background-color: #C8E6C9;
                selection-color: #000000;
            }
            /* Hover sobre los ítems */
            QComboBox QAbstractItemView::item:hover {
                background-color: #E6F4EA;
                color: #000000;
            }

            /* Botones */
            QPushButton {
                font-size: 14px;
                padding: 8px 15px;
                border-radius: 6px;
                border: 1px solid transparent;
                font-weight: 500;
            }

            /* Guardar */
            QPushButton:default {
                background-color: #4CAF50;
                color: #FFFFFF;
            }
            QPushButton:default:hover {
                background-color: #45A049;
            }

            /* Cancelar */
            QPushButton:!default {
                background-color: #F5F5F5;
                color: #333333;
                border: 1px solid #CCCCCC;
            }
            QPushButton:!default:hover {
                background-color: #FFEBEE;
                border: 1px solid #E57373;
                color: #C62828;
            }
        """)

        # Efecto de sombra suave alrededor del cuadro
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setOffset(0, 0)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(sombra)

        # --- Lógica de datos ---
        self.config_modificada = config_actual["gestos"].copy()
        self.acciones_disponibles = [accion["nombre"] for accion in config_actual["acciones"][1:]]

        # --- Layout principal ---
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Texto superior
        info_label = QLabel("Seleccione un gesto y asigne la acción correspondiente:")
        info_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #333333;")
        layout.addWidget(info_label)

        # ComboBox de gestos
        self.combo_gestos = QComboBox()
        layout.addWidget(QLabel("Gesto:"))
        layout.addWidget(self.combo_gestos)

        # ComboBox de acciones
        self.combo_acciones = QComboBox()
        layout.addWidget(QLabel("Acción:"))
        layout.addWidget(self.combo_acciones)

        layout.addStretch(1)

        # Botones Guardar / Cancelar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Save).setDefault(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # --- Inicialización de datos ---
        self.cargar_datos_iniciales()
        self.combo_gestos.currentIndexChanged.connect(self.actualizar_combo_acciones)
        self.combo_acciones.currentIndexChanged.connect(self.registrar_cambio_accion)

    # --- Métodos funcionales ---
    def cargar_datos_iniciales(self):
        """Puebla los ComboBox con los datos iniciales del config."""
        emojis = {
            "Mano abierta": "✋🏻",
            "Puno cerrado": "✊🏻",
            "Apuntar": "👉🏻",
            "Paz": "✌🏻",
            "Cuernos": "🤘🏻",
            "Llamame": "🤙🏻",
            "Pulgar abajo": "👎🏻",
            "Ok": "👌🏻",
            "Gesto extra 1": "☝🏻",
            "Gesto extra 2": "🤞🏻",
        }
        gestos_editables = [f'{emojis[gesto["nombre"]]} {gesto["nombre"]}' for gesto in self.config_modificada[1:]]
        self.combo_gestos.addItems(gestos_editables)
        self.combo_acciones.addItems(self.acciones_disponibles)
        self.actualizar_combo_acciones()

    def actualizar_combo_acciones(self):
        """Al cambiar de gesto, muestra la acción que tiene asignada actualmente."""
        gesto_seleccionado = next((gesto for gesto in self.config_modificada if gesto["nombre"] == self.combo_gestos.currentText()), None)
        if gesto_seleccionado:
            accion_actual = self.acciones_disponibles[gesto_seleccionado["accion"] - 1]
            self.combo_acciones.setCurrentText(accion_actual)

    def registrar_cambio_accion(self):
        """Actualiza el diccionario en memoria cuando el usuario cambia una acción."""
        gesto_seleccionado = next((gesto for gesto in self.config_modificada if gesto["nombre"] == self.combo_gestos.currentText()), None)
        accion_seleccionada = next((i + 1 for i, accion in enumerate(self.acciones_disponibles) if accion == self.combo_acciones.currentText()), None)
        if gesto_seleccionado and accion_seleccionada:
            gesto_seleccionado['accion'] = accion_seleccionada

    def obtener_config_actualizada(self):
        """Método para que la ventana principal obtenga la configuración final."""
        return self.config_modificada
