import sys
import cv2
import json
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from motor_vision import MotorVision
from ui_dialogo_modificar import DialogoModificar
from ui_dialogo_lista import DialogoListaGestos
import acciones as ac
from overlay_visual import OverlayVisual
from estilos import HOJA_ESTILO

class BarraTitulo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BarraTitulo")
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Título
        self.titulo = QLabel("GESTUS CONTROL // CYBERPUNK_EDITION")
        self.titulo.setObjectName("TituloApp")
        layout.addWidget(self.titulo)
        
        layout.addStretch()
        
        # Botones
        self.btn_min = QPushButton("_")
        self.btn_min.setObjectName("BotonControl")
        self.btn_min.setFixedSize(40, 40)
        self.btn_min.clicked.connect(parent.showMinimized)
        layout.addWidget(self.btn_min)
        
        self.btn_close = QPushButton("X")
        self.btn_close.setObjectName("BotonControl")
        self.btn_close.setObjectName("BotonCerrar") # ID específico para estilo rojo
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.clicked.connect(parent.close)
        layout.addWidget(self.btn_close)
        
        # Variables para mover ventana
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.window().move(self.window().pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None

class GestusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestusControl - Cyberpunk Edition")
        
        # Configuración Frameless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1100, 700)
        
        self.setStyleSheet(HOJA_ESTILO)

        self.vision_activa = False
        self.hilo_vision = None
        
        self.overlay = OverlayVisual()
        self.overlay.hide()

        # Widget central principal (contenedor de todo)
        self.widget_central = QWidget()
        self.widget_central.setObjectName("FondoPrincipal") # Para aplicar borde/fondo
        self.setCentralWidget(self.widget_central)
        
        # Layout Principal (Vertical: Barra Título + Contenido)
        self.layout_principal = QVBoxLayout(self.widget_central)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)
        
        # 1. Barra de Título
        self.barra_titulo = BarraTitulo(self)
        self.layout_principal.addWidget(self.barra_titulo)
        
        # 2. Contenido (Horizontal: Video + Panel)
        self.contenido_layout = QHBoxLayout()
        self.contenido_layout.setContentsMargins(20, 20, 20, 20)
        self.contenido_layout.setSpacing(20)
        self.layout_principal.addLayout(self.contenido_layout)

        # --- Panel Izquierdo: Video ---
        self.panel_video = QWidget()
        self.layout_video = QVBoxLayout(self.panel_video)
        self.layout_video.setContentsMargins(0, 0, 0, 0)
        
        self.etiqueta_video = QLabel("Cámara apagada")
        self.etiqueta_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etiqueta_video.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.etiqueta_video.setStyleSheet("background-color: black; color: white; font-size: 24px; border: 2px solid #00E5FF; border-radius: 10px;")
        self.layout_video.addWidget(self.etiqueta_video)
        
        self.contenido_layout.addWidget(self.panel_video, 65)

        # --- Panel Derecho: Controles ---
        self.panel_control = QWidget()
        self.panel_control.setObjectName("PanelDerecho")
        self.layout_derecho = QVBoxLayout(self.panel_control)
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
        self.boton_inicio = QPushButton("📷  INICIAR SISTEMA")
        self.boton_inicio.setObjectName("BotonAccion")
        self.boton_inicio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_inicio.clicked.connect(self.toggle_camara)
        self.layout_derecho.addWidget(self.boton_inicio)

        # --- Botones secundarios ---
        layout_botones = QHBoxLayout()
        boton_ver_todos = QPushButton("👁️  VER GESTOS")
        boton_modificar = QPushButton("⚙️  CONFIGURAR")
        self.boton_mouse = QPushButton("🖱️  MOUSE")
        self.boton_mouse.setCheckable(True)

        for boton in [boton_ver_todos, boton_modificar, self.boton_mouse]:
            boton.setCursor(Qt.CursorShape.PointingHandCursor)
            layout_botones.addWidget(boton)

        self.layout_derecho.addLayout(layout_botones)

        boton_ver_todos.clicked.connect(self.abrir_dialogo_lista)
        boton_modificar.clicked.connect(self.abrir_dialogo_modificar)
        self.boton_mouse.clicked.connect(self.toggle_mouse_mode)

        self.contenido_layout.addWidget(self.panel_control, 35)

    # =========================
    #  MÉTODOS DE FUNCIONALIDAD
    # =========================
    def toggle_camara(self):
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
            self.overlay.showFullScreen()
            self.vision_activa = True

            self.boton_inicio.setText("🛑  FINALIZAR SISTEMA")
            self.boton_inicio.setStyleSheet("background-color: #FF1744; color: white; border: none;") 
            self.etiqueta_video.setText("Iniciando sensores...")
            self.refrescar_panel_gestos()
        else:
            # Detener cámara
            if self.hilo_vision:
                self.hilo_vision.stop()
                self.hilo_vision = None
            self.vision_activa = False
            self.overlay.hide()

            self.etiqueta_video.clear()
            self.etiqueta_video.setText("Sistema en espera.")
            self.etiqueta_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.etiqueta_video.setStyleSheet("background-color: black; color: white; font-size: 24px; border: 2px solid #00E5FF; border-radius: 10px;")

            self.boton_inicio.setText("📷  INICIAR SISTEMA")
            self.boton_inicio.setStyleSheet("")
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
                self.boton_mouse.setText("🖱️  MOUSE ACTIVO")
                self.boton_mouse.setStyleSheet("background-color: #00E5FF; color: #121212; border: 2px solid #FFFFFF;")
                self.overlay.set_estado("Modo Mouse")
            else:
                self.boton_mouse.setText("🖱️  MOUSE")
                self.boton_mouse.setStyleSheet("") # Restaurar estilo default
                self.overlay.set_estado("Esperando")
        else:
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
        self.overlay.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GestusApp()
    ventana.show()
    sys.exit(app.exec())
