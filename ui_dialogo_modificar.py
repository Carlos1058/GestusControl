# ui_dialogo_modificar.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QComboBox, QDialogButtonBox, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor
from estilos import HOJA_ESTILO


class DialogoModificar(QDialog):
    def __init__(self, config_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modificar Asignación de Gestos")
        self.setMinimumSize(500, 250)
        self.setStyleSheet(HOJA_ESTILO)

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
        info_label.setObjectName("InfoTexto")
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
        button_box.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
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
        gestos_editables = [f'{gesto["emoji"]} {gesto["nombre"]}' for gesto in self.config_modificada[1:]]
        self.combo_gestos.addItems(gestos_editables)
        self.combo_acciones.addItems(self.acciones_disponibles)
        self.actualizar_combo_acciones()

    def actualizar_combo_acciones(self):
        """Al cambiar de gesto, muestra la acción que tiene asignada actualmente."""
        nombre_gesto = self.combo_gestos.currentText().split(" ", 1)[1]
        gesto_seleccionado = next((gesto for gesto in self.config_modificada if gesto["nombre"] == nombre_gesto), None)
        if gesto_seleccionado:
            accion_actual = self.acciones_disponibles[gesto_seleccionado["accion"] - 1]
            self.combo_acciones.setCurrentText(accion_actual)

    def registrar_cambio_accion(self):
        """Actualiza el diccionario en memoria cuando el usuario cambia una acción."""
        nombre_gesto = self.combo_gestos.currentText().split(" ", 1)[1]
        gesto_seleccionado = next((gesto for gesto in self.config_modificada if gesto["nombre"] == nombre_gesto), None)
        accion_seleccionada = next((i + 1 for i, accion in enumerate(self.acciones_disponibles) if accion == self.combo_acciones.currentText()), None)
        if gesto_seleccionado and accion_seleccionada:
            gesto_seleccionado['accion'] = accion_seleccionada

    def obtener_config_actualizada(self):
        """Método para que la ventana principal obtenga la configuración final."""
        return self.config_modificada
