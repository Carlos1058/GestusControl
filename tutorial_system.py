from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class TutorialManager(QObject):
    """
    Gestiona los estados y el flujo del tutorial interactivo.
    """
    sig_actualizar_instruccion = pyqtSignal(str, str) 
    sig_resaltar_ui = pyqtSignal(str) 
    sig_tutorial_finalizado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activo = False
        self.paso_actual = 0

        # Flujo Expandido
        self.pasos = [
            "INTRO",          
            "ENCENDER_CAMARA",
            "INFO_CAMARA",
            "DETECTAR_MANO",
            "EXPLICACION_GESTOS", # Nuevo: Intro a gestos
            "PRUEBA_GESTO_1",     # Paz 
            "PRUEBA_GESTO_2",     # Nuevo: Like
            "INFO_PERSONALIZACION", # Nuevo: Explicar config
            "MODO_MOUSE",     
            "EXPLICACION_MOUSE",  # Nuevo: Explicar Dwell Click
            "FIN"
        ]

        # Gestos objetivos para validación en run-time
        self.gesto_objetivo_actual = "" 

    def iniciar(self):
        self.activo = True
        self.paso_actual = 0
        self.ejecutar_paso()

    def detener(self):
        self.activo = False
        self.sig_actualizar_instruccion.emit("", "") 
        self.sig_resaltar_ui.emit("") 

    def siguiente_paso(self):
        if not self.activo: return
        self.paso_actual += 1
        if self.paso_actual >= len(self.pasos):
            self.finalizar()
        else:
            self.ejecutar_paso()

    def ejecutar_paso(self):
        paso = self.pasos[self.paso_actual]

        if paso == "INTRO":
            self.sig_actualizar_instruccion.emit("BIENVENIDO A GESTUS", "El futuro del control sin contacto.\nVamos a configurarlo juntos.")
            self.sig_resaltar_ui.emit("")
            QTimer.singleShot(4000, self.siguiente_paso)

        elif paso == "ENCENDER_CAMARA":
            self.sig_actualizar_instruccion.emit("PASO 1: ACTIVACIÓN", "Haz click en 'Iniciar Cámara'.\nEsto activa tu motor de visión.")
            self.sig_resaltar_ui.emit("btn_camara")

        elif paso == "INFO_CAMARA":
            self.sig_actualizar_instruccion.emit("TIP DE SEGURIDAD", "Puedes apagar la cámara en cualquier momento\npulsando el mismo botón.")
            self.sig_resaltar_ui.emit("btn_camara")
            QTimer.singleShot(4000, self.siguiente_paso)

        elif paso == "DETECTAR_MANO":
            self.sig_actualizar_instruccion.emit("PASO 2: CONEXIÓN", "Levanta tu mano frente a la cámara.\nAsegúrate de tener buena luz.")
            self.sig_resaltar_ui.emit("")

        elif paso == "EXPLICACION_GESTOS":
            self.sig_actualizar_instruccion.emit("GESTOS MÁGICOS", "Cada gesto ejecuta una acción.\nVamos a probar algunos.")
            self.sig_resaltar_ui.emit("")
            QTimer.singleShot(5000, self.siguiente_paso)

        elif paso == "PRUEBA_GESTO_1":
            self.gesto_objetivo_actual = "Paz"
            self.sig_actualizar_instruccion.emit("PRUEBA 1", f"Haz 'Amor y Paz' ✌️y mantén.\nEspera el borde verde para confirmar.\nEsto abrirá el Menú Inicio.")
            self.sig_resaltar_ui.emit("")

        elif paso == "PRUEBA_GESTO_2":
            self.gesto_objetivo_actual = "Like"
            self.sig_actualizar_instruccion.emit("PRUEBA 2", f"Haz un 'Like' 👍 y mantén.\nEspera el borde verde para confirmar. \nEsto cambia de canción.")
            self.sig_resaltar_ui.emit("")

        elif paso == "INFO_PERSONALIZACION":
            self.sig_actualizar_instruccion.emit(
                "PERSONALIZACIÓN", "En el panel de configuración verás\nlistas desplegables junto a cada gesto.\nÚsalas y explora las opciones de acción")
            self.sig_resaltar_ui.emit("btn_menu")
            QTimer.singleShot(10000, self.siguiente_paso)

        elif paso == "MODO_MOUSE":
            self.sig_actualizar_instruccion.emit("PASO 3: MOUSE", "Activa el 'Modo Mouse' en el dock\npara controlar el cursor.")
            self.sig_resaltar_ui.emit("btn_mouse")

        elif paso == "EXPLICACION_MOUSE":
            self.sig_actualizar_instruccion.emit("¿CÓMO HACER CLICK?", "Mueve con tu dedo índice.\nMANTÉN FIJO para hacer Click.")
            self.sig_resaltar_ui.emit("")
            QTimer.singleShot(6000, self.siguiente_paso)

        elif paso == "FIN":
            self.finalizar()

    def finalizar(self):
        self.sig_actualizar_instruccion.emit("TUTORIAL COMPLETADO", "Ahora tienes el control total.\n¡Explora GestusControl!")
        self.sig_resaltar_ui.emit("")
        QTimer.singleShot(5000, self.detener)
        self.sig_tutorial_finalizado.emit()

    # --- Event listeners ---

    def evento_camara_encendida(self):
        if self.activo and self.pasos[self.paso_actual] == "ENCENDER_CAMARA":
            self.siguiente_paso()

    def evento_mano_detectada(self):
        if self.activo and self.pasos[self.paso_actual] == "DETECTAR_MANO":
            self.siguiente_paso()

    def evento_gesto_reconocido(self, nombre_gesto):
        # Validar gestos dinámicamente según el paso actual
        if self.activo and "PRUEBA_GESTO" in self.pasos[self.paso_actual]:
            if nombre_gesto == self.gesto_objetivo_actual:
                self.sig_actualizar_instruccion.emit("¡CORRECTO!", f"Gesto {nombre_gesto} detectado.")
                QTimer.singleShot(2000, self.siguiente_paso)

    def evento_mouse_activado(self):
        if self.activo and self.pasos[self.paso_actual] == "MODO_MOUSE":
            self.siguiente_paso()
