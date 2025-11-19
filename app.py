import sys
import cv2
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from motor_vision import MotorVision
from ui_dialogo_modificar import DialogoModificar
from ui_dialogo_lista import DialogoListaGestos
import acciones as ac
import random
from overlay_visual import OverlayVisual
from estilos import HOJA_ESTILO

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestusControl - Cyberpunk Edition")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet(HOJA_ESTILO)

        self.vision_activa = False  # Estado de la cámara
        self.hilo_vision = None     # Inicialmente no hay hilo
        
        # Inicializar Overlay (oculto al principio)
        self.overlay = OverlayVisual()
        self.overlay.hide()

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- Etiqueta de video ---
        self.etiqueta_video = QLabel("Cámara no iniciada")
        self.etiqueta_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etiqueta_video.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        # El estilo se define en estilos.py, pero mantenemos el fondo negro para el video
        self.etiqueta_video.setStyleSheet("background-color: black; color: white; font-size: 24px; border: 2px solid #00E5FF; border-radius: 10px;")
        layout_principal.addWidget(self.etiqueta_video, 3)

        # --- Panel derecho ---
        panel_derecho = QWidget()
        panel_derecho.setObjectName("PanelDerecho") # Para aplicar estilo CSS
        self.layout_derecho = QVBoxLayout(panel_derecho)
        self.layout_derecho.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_derecho.setSpacing(10)

        titulo_gestos = QLabel("Gestos Sugeridos")
        titulo_gestos.setObjectName("Titulo")
        self.layout_derecho.addWidget(titulo_gestos)

        self.contenedor_gestos = QWidget()
        self.layout_gestos = QVBoxLayout(self.contenedor_gestos)
        self.layout_derecho.addWidget(self.contenedor_gestos)
        self.refrescar_panel_gestos()

        self.layout_derecho.addStretch(1)
        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout_derecho.addWidget(linea)

        titulo_estado = QLabel("Estado en Vivo")
        titulo_estado.setObjectName("Subtitulo")
        self.layout_derecho.addWidget(titulo_estado)

        self.info_estado = QLabel()
        self.info_gesto_detectado = QLabel()
        self.info_feedback = QLabel()
        for label in [self.info_estado, self.info_gesto_detectado, self.info_feedback]:
            label.setObjectName("InfoTexto")
            label.setWordWrap(True)
            self.layout_derecho.addWidget(label)

        self.layout_derecho.addStretch(1)

        # --- Botón Iniciar/Finalizar ---
        self.boton_inicio = QPushButton("Iniciar Sistema")
        self.boton_inicio.setObjectName("BotonAccion")
        self.boton_inicio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_inicio.clicked.connect(self.toggle_camara)
        self.layout_derecho.addWidget(self.boton_inicio)

        # --- Botones secundarios ---
        layout_botones = QHBoxLayout()
        boton_ver_todos = QPushButton("Ver Todos los Gestos")
        boton_modificar = QPushButton("Modificar Gestos")
        self.boton_mouse = QPushButton("Activar Mouse")
        self.boton_mouse.setCheckable(True)

        for boton in [boton_ver_todos, boton_modificar, self.boton_mouse]:
            # Estilo manejado por CSS global (QPushButton)
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            layout_botones.addWidget(boton)

        self.layout_derecho.addLayout(layout_botones)

        boton_ver_todos.clicked.connect(self.abrir_dialogo_lista)
        boton_modificar.clicked.connect(self.abrir_dialogo_modificar)
        self.boton_mouse.clicked.connect(self.toggle_mouse_mode)

        layout_principal.addWidget(panel_derecho, 1)

    # =========================
    #  MÉTODOS DE FUNCIONALIDAD
    # =========================
    def toggle_camara(self):
        """Activa o desactiva la cámara y actualiza el botón."""
        if not self.vision_activa:
            # Iniciar cámara
            self.hilo_vision = MotorVision()
            self.hilo_vision.cambio_de_frame.connect(self.actualizar_frame)
            self.hilo_vision.actualizacion_feedback.connect(self.actualizar_feedback_panel)
            
            # Conectar señales del Overlay
            self.hilo_vision.gesto_progreso.connect(lambda p: self.overlay.set_estado("Detectando", p))
            self.hilo_vision.gesto_confirmado_signal.connect(lambda g: self.overlay.set_estado("Confirmado"))
            self.hilo_vision.gesto_cancelado_signal.connect(lambda: self.overlay.set_estado("Cancelado"))
            
            self.hilo_vision.start()
            self.overlay.showFullScreen() # Mostrar overlay al iniciar cámara
            self.vision_activa = True

            # Cambiar estilo del botón
            self.boton_inicio.setText("Finalizar Sistema")
            # El color rojo/magenta se puede manejar dinámicamente o dejar que el estilo "BotonAccion" lo maneje.
            # Para feedback visual de "Parar", podemos cambiar el estilo inline momentáneamente o confiar en el texto.
            self.boton_inicio.setStyleSheet("background-color: #FF1744; color: white; border: none;") 
            
            self.etiqueta_video.setText("Iniciando sensores...")

            self.refrescar_panel_gestos()
        else:
            # Detener cámara
            if self.hilo_vision:
                self.hilo_vision.stop()
                self.hilo_vision = None
            self.vision_activa = False
            self.overlay.hide() # Ocultar overlay

            # Limpiar QLabel para que no quede la última imagen
            self.etiqueta_video.clear()
            self.etiqueta_video.setText("Sistema en espera.")
            self.etiqueta_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Restaurar borde neon
            self.etiqueta_video.setStyleSheet("background-color: black; color: white; font-size: 24px; border: 2px solid #00E5FF; border-radius: 10px;")

            # Restaurar botón
            self.boton_inicio.setText("Iniciar Sistema")
            self.boton_inicio.setStyleSheet("") # Restaurar al estilo de la hoja de estilos (ID BotonAccion)
            
            self.refrescar_panel_gestos()

    def refrescar_panel_gestos(self):
        while self.layout_gestos.count():
            item = self.layout_gestos.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                gestos_a_mostrar = random.sample(config["gestos"][1:-2], min(3, len(config["gestos"])))
                for gesto in gestos_a_mostrar:
                    nombre_gesto = gesto["nombre"]
                    descripcion_gesto = config["acciones"][gesto["accion"]]["descripcion"]
                    label_gesto = QLabel(f"▪ {gesto.get('emoji', '')} {nombre_gesto}\n    > {descripcion_gesto}")
                    label_gesto.setObjectName("InfoTexto")
                    label_gesto.setWordWrap(True)
                    self.layout_gestos.addWidget(label_gesto)
        except Exception as e:
            self.layout_gestos.addWidget(QLabel(f"Error: {e}"))

    def abrir_dialogo_lista(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                gestos = config["gestos"]
                acciones = config["acciones"]
            dialogo = DialogoListaGestos(gestos, acciones, self)
            dialogo.exec()
        except Exception as e:
            print(f"Error al abrir la lista de gestos: {e}")

    def abrir_dialogo_modificar(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)

            #!acciones = list(ac.MAPA_ACCIONES.keys())
            dialogo = DialogoModificar(config, self)
            if dialogo.exec():
                config["gestos"] = dialogo.obtener_config_actualizada()
                with open("config.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.refrescar_panel_gestos()
        except Exception as e:
            print(f"Error al abrir el diálogo de modificación: {e}")

    def toggle_mouse_mode(self):
        if self.hilo_vision and self.vision_activa:
            modo_activo = self.hilo_vision.toggle_modo_mouse()
            if modo_activo:
                self.boton_mouse.setText("Desactivar Mouse")
                self.boton_mouse.setStyleSheet("background-color: #00E5FF; color: #121212;")
                self.overlay.set_estado("Modo Mouse")
            else:
                self.boton_mouse.setText("Activar Mouse")
                self.boton_mouse.setStyleSheet("") # Restaurar estilo default
                self.overlay.set_estado("Esperando")
        else:
            # Si la cámara no está activa, no permitir activar mouse (o activarla automáticamente)
            self.boton_mouse.setChecked(False)
            self.info_estado.setText("Error: Inicia la cámara primero")

    def actualizar_feedback_panel(self, estado, gesto, feedback):
        self.info_estado.setText(f"<b>Estado:</b> {estado}")
        self.info_gesto_detectado.setText(f"<b>Detectando:</b> {gesto}")
        self.info_feedback.setText(f"<b>Feedback:</b> {feedback}")

    def actualizar_frame(self, frame_cv_bgr):
        frame_rgb = cv2.cvtColor(frame_cv_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_por_linea = ch * w
        imagen_qt = QImage(frame_rgb.data, w, h, bytes_por_linea, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(imagen_qt)
        pixmap_escalado = pixmap.scaled(
            self.etiqueta_video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.etiqueta_video.setPixmap(pixmap_escalado)

    def close_event(self, event):
        if self.hilo_vision:
            self.hilo_vision.stop()
        self.overlay.close() # Asegurar que se cierre el overlay
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
