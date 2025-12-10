import sys
import cv2
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QSizePolicy, QComboBox)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer
from motor_vision import MotorVision
from overlay_visual import OverlayVisual
from tutorial_system import TutorialManager

class GestusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestusControl")
        self.setGeometry(100, 100, 1280, 720)

        # Cargar estilos
        try:
            with open("styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Advertencia: styles.qss no encontrado.")

        # Estado
        self.camara_activa = False
        self.modo_mouse_activo = False
        self.sidebar_expanded = False
        self.tutorial_activo = False

        # --- UI SETUP V2 ---
        self.setup_ui_v2()

        # Motor de Visión
        self.hilo_vision = MotorVision()
        self.hilo_vision.cambio_de_frame.connect(self.actualizar_imagen)
        self.hilo_vision.actualizacion_feedback.connect(self.actualizar_feedback_toast) # Nuevo slot para Toasts
        self.hilo_vision.gesto_progreso.connect(self.overlay.set_progreso_gesto)
        self.hilo_vision.gesto_confirmado_signal.connect(self.mostrar_confirmacion_gesto)
        self.hilo_vision.gesto_cancelado_signal.connect(self.overlay.reset_progreso)
        self.hilo_vision.dwell_progreso.connect(self.overlay.set_dwell_estado)
        self.hilo_vision.gesto_confirmado_signal.connect(self.on_gesto_confirmado) # Modificado
        self.hilo_vision.mano_detectada.connect(self.on_mano_detectada)

        self.hilo_vision.solicitud_toggle_modo.connect(self.alternar_modo_mouse)
        self.hilo_vision.solicitud_cierre.connect(self.cerrar_aplicacion)

        # Tutorial System
        self.tutorial = TutorialManager()

        self.tutorial.sig_actualizar_instruccion.connect(self.overlay.set_tutorial_info)
        self.tutorial.sig_senalar_ui.connect(self.senalar_widget)
        self.tutorial.sig_resaltar_ui.connect(self.resaltar_widget)
        self.tutorial.sig_tutorial_finalizado.connect(self.on_tutorial_finalizado)

    def setup_ui_v2(self):
        """Configura la interfaz moderna con Dock y Sidebar."""
        # Widget central que contiene todo (Overlay Layout)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal: Stacked para poner UI sobre Video, o Absolute
        # Usaremos un layout principal con márgenes 0 y un overlay manual
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. Contenedor de Video (Fondo)
        self.video_container = QLabel("Cámara Inactiva")
        self.video_container.setObjectName("VideoContainer")
        self.video_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # IMPORTANTE: Ignored evita que el QLabel fuerce el tamaño de la ventana al cambiar el pixmap
        self.video_container.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.main_layout.addWidget(self.video_container)

        # 2. Overlay Visual (Transparente, encima del video)
        # Nota: En esta arquitectura simplificada, el OverlayVisual se pinta SOBRE el video_container
        # o usamos una ventana transparente separada. Por simplicidad y robustez, usaremos
        # el OverlayVisual como un widget hijo del video_container o encima de él.
        # Para V2, mantendremos el OverlayVisual como ventana independiente 'AlwaysOnTop'
        # controlada por app.py, ya que funcionó bien para el Dwell Click.
        self.overlay = OverlayVisual()
        # El overlay se posicionará dinámicamente sobre el video_container en resizeEvent si quisiéramos,
        # pero el diseño actual de OverlayVisual es "pantalla completa transparente".
        # Lo dejaremos así para que cubra todo.

        # 3. Dock Flotante (Abajo)
        self.dock_widget = QFrame(self)
        self.dock_widget.setObjectName("FloatingDock")
        dock_layout = QHBoxLayout(self.dock_widget)
        dock_layout.setContentsMargins(20, 10, 20, 10)
        dock_layout.setSpacing(20)

        # Botones del Dock
        self.btn_camara = self.crear_boton_dock("📷 Iniciar", self.toggle_camara, checkable=True)
        self.btn_mouse = self.crear_boton_dock("🖱️ Mouse", self.toggle_mouse_mode, checkable=True)
        self.btn_menu = self.crear_boton_dock("⚙️ Gestos", self.toggle_sidebar, checkable=True)
        self.btn_tutorial = self.crear_boton_dock("🎓 Tutorial", self.iniciar_tutorial)
        self.btn_salir = self.crear_boton_dock("❌ Salir", self.close)
        self.btn_salir.setObjectName("ExitButton")

        dock_layout.addWidget(self.btn_camara)
        dock_layout.addWidget(self.btn_mouse)
        dock_layout.addWidget(self.btn_menu)
        dock_layout.addWidget(self.btn_tutorial)
        dock_layout.addWidget(self.btn_salir)

        # 4. Sidebar (Derecha)
        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(0) # Inicialmente colapsado
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        lbl_gestos = QLabel("Configuración de Gestos")
        lbl_gestos.setObjectName("SidebarHeader")
        sidebar_layout.addWidget(lbl_gestos)

        # Scroll Area para los gestos
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(15)

        scroll.setWidget(scroll_content)
        sidebar_layout.addWidget(scroll)

        # Construir la lista de gestos dinámicamente
        self.construir_sidebar_gestos()

        # Botón Guardar
        btn_guardar = QPushButton("💾 Guardar Cambios")
        btn_guardar.setObjectName("ActionBtn")
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.clicked.connect(self.guardar_configuracion)
        btn_guardar.clicked.connect(self.guardar_configuracion)
        sidebar_layout.addWidget(btn_guardar)

        # 5. Toast Notification (Arriba Centro)
        self.toast = QLabel(self)
        self.toast.setObjectName("Toast")
        self.toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast.hide()
        self.toast_timer = QTimer()
        self.toast_timer.setSingleShot(True)
        self.toast_timer.timeout.connect(self.ocultar_toast)

    def crear_boton_dock(self, texto, funcion, checkable=False):
        btn = QPushButton(texto)
        btn.setObjectName("DockButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if checkable:
            btn.setCheckable(True)
        btn.clicked.connect(funcion)
        return btn

    def resizeEvent(self, event):
        # Posicionar Dock (Abajo Centro)
        dock_w = 570
        dock_h = 60
        self.dock_widget.setGeometry(
            (self.width() - dock_w) // 2,
            self.height() - dock_h - 30,
            dock_w,
            dock_h
        )

        # Posicionar Sidebar (Derecha, Altura completa)
        sidebar_w = 300 if self.sidebar_expanded else 0
        self.sidebar.setGeometry(
            self.width() - sidebar_w,
            0,
            sidebar_w,
            self.height()
        )

        # Posicionar Toast (Arriba Centro)
        self.toast.setGeometry(
            (self.width() - 400) // 2,
            40,
            400,
            40
        )
        super().resizeEvent(event)

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        # Animación simple
        width = 250 if self.sidebar_expanded else 0
        self.sidebar.setFixedWidth(width)
        # Forzar resize para actualizar geometría
        self.resizeEvent(None)

        if self.sidebar_expanded:
            self.tutorial.evento_menu_abierto()

    def show_toast(self, mensaje):
        self.toast.setText(mensaje)
        self.toast.show()
        self.toast.raise_()
        self.toast_timer.start(2500) # 2.5 segundos

    def ocultar_toast(self):
        self.toast.hide()

    def actualizar_feedback_toast(self, estado, gesto, progreso):
        # Lógica inteligente para no saturar de toasts
        if gesto != "Desconocido" and gesto != "":
            # Solo mostrar si es un gesto nuevo o importante
            pass 

        # Si hay un cambio de estado importante, mostrar toast
        if estado == "Confirmado":
            self.show_toast(f"✅ Gesto Confirmado: {gesto}")

    def mostrar_confirmacion_gesto(self, nombre_gesto):
        self.show_toast(f"🚀 Ejecutando: {nombre_gesto}")
        self.overlay.mostrar_confirmacion(nombre_gesto)

    def on_gesto_confirmado(self, nombre_gesto):
        """Wrapper para manejar lógica extra al confirmar gesto."""
        self.mostrar_confirmacion_gesto(nombre_gesto)
        self.tutorial.evento_gesto_reconocido(nombre_gesto)

    def on_mano_detectada(self):
        self.tutorial.evento_mano_detectada()

    def iniciar_tutorial(self):
        if not self.tutorial_activo:
            self.tutorial_activo = True
            self.btn_tutorial.setStyleSheet("""
                QPushButton#DockButton {
                    background-color: rgba(0, 229, 255, 50); 
                    border: 2px solid #00e5ff;
                    color: #00e5ff;
                }
            """)

            if self.modo_mouse_activo:
                self.toggle_mouse_mode()

            if self.camara_activa:
                self.btn_camara.setChecked(False)
                self.camara_activa = False
                self.btn_camara.setText("📷 Iniciar")

            if self.sidebar_expanded:
                self.toggle_sidebar()
                self.btn_menu.setChecked(False)

            self.tutorial.iniciar()

    def on_tutorial_finalizado(self):
        self.tutorial_activo = False
        self.btn_tutorial.setStyleSheet("")
        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())
        self.show_toast("🎓 Tutorial Completado")

    def senalar_widget(self, nombre_widget):
        estilo_senalado = """
            QPushButton#DockButton {
                background-color: rgba(60, 200, 60, 50);
                border: 3px solid #32CD32; 
            }
        """

        widgets = {
            "btn_camara": self.btn_camara,
            "btn_mouse": self.btn_mouse,
            "btn_menu": self.btn_menu,
        }

        # Primero limpiar todos
        for w in widgets.values():
            w.setStyleSheet("")

        if nombre_widget in widgets:
            widgets[nombre_widget].setStyleSheet(estilo_senalado)

    def resaltar_widget(self, nombre_widget):
        estilo_resaltado = """
            QPushButton#DockButton {
                background-color: rgba(0, 229, 255, 20);
                border: 2px solid #00e5ff;
            }
        """

        widgets = {
            "btn_camara": self.btn_camara,
            "btn_mouse": self.btn_mouse,
            "btn_menu": self.btn_menu
        }

        # Primero limpiar todos
        for w in widgets.values():
            w.setStyleSheet("") 

        if nombre_widget in widgets:
            widgets[nombre_widget].setStyleSheet(estilo_resaltado)

    def toggle_camara(self):
        if not self.camara_activa:
            self.hilo_vision.start()
            self.camara_activa = True
            self.btn_camara.setText("⏹ Detener")
            self.btn_camara.setChecked(True)
            self.overlay.show() # Mostrar overlay al iniciar
            self.show_toast("Cámara Iniciada")
            self.tutorial.evento_camara_encendida()

        else:
            self.hilo_vision.stop()
            self.camara_activa = False
            self.video_container.setPixmap(QPixmap())
            self.video_container.setText("Cámara Inactiva")
            self.btn_camara.setText("📷 Iniciar")
            self.btn_camara.setChecked(False)
            self.overlay.hide()
            self.show_toast("Cámara Detenida")

    def toggle_mouse_mode(self):
        if not self.camara_activa:
            self.show_toast("⚠️ Enciende la cámara primero")
            self.btn_mouse.setChecked(False)
            return

        activo = self.hilo_vision.toggle_modo_mouse()
        self.modo_mouse_activo = activo
        self.btn_mouse.setChecked(activo)

        if activo:
            self.show_toast("🖱️ Modo Mouse: ACTIVO")
            self.overlay.mostrar_mensaje_centro("MODO MOUSE")
            self.tutorial.evento_mouse_activado()

        else:
            self.show_toast("✋ Modo Gestos: ACTIVO")
            self.overlay.mostrar_mensaje_centro("MODO GESTOS")

    def actualizar_imagen(self, frame):
        # Escalar frame al tamaño del contenedor manteniendo aspecto
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        # Escalar al tamaño del video_container
        scaled_pixmap = pixmap.scaled(
            self.video_container.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_container.setPixmap(scaled_pixmap)

    def construir_sidebar_gestos(self):
        """Construye la lista de gestos con ComboBoxes dinámicamente."""
        # Limpiar layout anterior si existe
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Cargar config actual
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {"acciones": [], "gestos": []}

        self.combos_gestos = {} # Para guardar referencias a los combos

        acciones_disponibles = [a["nombre"] for a in config["acciones"]]

        for gesture in config["gestos"]:
            # Contenedor por fila
            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0,0,0,0)
            row_layout.setSpacing(5)

            # Etiqueta: Emoji + Nombre
            lbl = QLabel(f"{gesture['emoji']} {gesture['nombre']}")
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
            row_layout.addWidget(lbl)

            # ComboBox de Acciones
            combo = QComboBox()
            combo.addItems(acciones_disponibles)

            # Seleccionar acción actual por NOMBRE
            accion_actual_nombre = gesture.get("accion_nombre", "Ninguna")
            index = combo.findText(accion_actual_nombre)
            if index >= 0:
                combo.setCurrentIndex(index)

            # Estilo del ComboBox
            combo.setStyleSheet(
                """
                QComboBox {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 14px;
                    width: 100px;
                }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: white;
                }
                
                QComboBox QAbstractItemView::item:hover {
                    background-color: rgba(0, 229, 255, 100);
                }
            """)

            row_layout.addWidget(combo)
            self.scroll_layout.addWidget(row_widget)

            # Guardar referencia: nombre_gesto -> combo
            self.combos_gestos[gesture["nombre"]] = combo

        self.scroll_layout.addStretch()

    def guardar_configuracion(self):
        """Guarda la configuración actual de los combos en el JSON."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Actualizar acciones en la config
            acciones_nombres = [a["nombre"] for a in config["acciones"]]

            for gesture in config["gestos"]:
                nombre = gesture["nombre"]
                if nombre in self.combos_gestos:
                    combo = self.combos_gestos[nombre]
                    nuevo_nombre_accion = combo.currentText()
                    gesture["accion_nombre"] = nuevo_nombre_accion
                    # Eliminamos 'accion' si existe para limpiar
                    if "accion" in gesture:
                        del gesture["accion"]

            # Guardar en archivo
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # Notificar al motor de visión para recargar
            self.hilo_vision.cargar_configuracion()

            self.show_toast("✅ Configuración Guardada")

        except Exception as e:
            print(f"Error guardando config: {e}")
            self.show_toast("❌ Error al guardar")

    def alternar_modo_mouse(self):
        """Accion para cambiar de modo gestos a mouse."""
        self.toggle_mouse_mode()

    def cerrar_aplicacion(self):
        QApplication.instance().quit()

    def closeEvent(self, event):
        if self.hilo_vision:
            self.hilo_vision.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GestusApp()
    ventana.show()
    sys.exit(app.exec())
