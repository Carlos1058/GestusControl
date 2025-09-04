import sys, cv2, json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QFrame)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from motor_vision import MotorVision 
from ui_dialogo_modificar import DialogoModificar
from ui_dialogo_lista import DialogoListaGestos # Nueva importación
import acciones as ac

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestus Control")
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet("background-color: #FFFFFF;")

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0,0,0,0); layout_principal.setSpacing(0)

        self.etiqueta_video = QLabel("Iniciando cámara..."); self.etiqueta_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.etiqueta_video.setStyleSheet("background-color: black;")
        layout_principal.addWidget(self.etiqueta_video, 3)

        panel_derecho = QWidget()
        panel_derecho.setStyleSheet("background-color: #F0F0F0; padding: 15px;")
        self.layout_derecho = QVBoxLayout(panel_derecho)
        self.layout_derecho.setAlignment(Qt.AlignmentFlag.AlignTop); self.layout_derecho.setSpacing(10)

        titulo_gestos = QLabel("Gestos Sugeridos")
        titulo_gestos.setStyleSheet("color: #000000; font-size: 22px; font-weight: bold;")
        self.layout_derecho.addWidget(titulo_gestos)
        
        self.contenedor_gestos = QWidget()
        self.layout_gestos = QVBoxLayout(self.contenedor_gestos)
        self.layout_derecho.addWidget(self.contenedor_gestos)
        self.refrescar_panel_gestos()

        self.layout_derecho.addStretch(1)
        linea = QFrame(); linea.setFrameShape(QFrame.Shape.HLine); linea.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout_derecho.addWidget(linea)
        
        titulo_estado = QLabel("Estado en Vivo")
        titulo_estado.setStyleSheet("color: #000000; font-size: 18px; font-weight: bold; margin-top: 10px;")
        self.layout_derecho.addWidget(titulo_estado)

        self.info_estado = QLabel(); self.info_gesto_detectado = QLabel(); self.info_feedback = QLabel()
        for label in [self.info_estado, self.info_gesto_detectado, self.info_feedback]:
            label.setStyleSheet("color: #333333; font-size: 14px;")
            label.setWordWrap(True)
            self.layout_derecho.addWidget(label)
        
        self.layout_derecho.addStretch(1)

        # Layout para los botones
        layout_botones = QHBoxLayout()
        boton_ver_todos = QPushButton("Ver Todos los Gestos")
        boton_modificar = QPushButton("Modificar Gestos")
        
        for boton in [boton_ver_todos, boton_modificar]:
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #E1E1E1; color: #000000; font-size: 14px;
                    padding: 10px; border-radius: 5px; border: 1px solid #CCCCCC;
                }
                QPushButton:hover { background-color: #D1D1D1; }
            """)
            layout_botones.addWidget(boton)

        self.layout_derecho.addLayout(layout_botones)
        
        boton_ver_todos.clicked.connect(self.abrir_dialogo_lista)
        boton_modificar.clicked.connect(self.abrir_dialogo_modificar)
        
        layout_principal.addWidget(panel_derecho, 1)

        self.hilo_vision = MotorVision()
        self.hilo_vision.cambio_de_frame.connect(self.actualizar_frame)
        self.hilo_vision.actualizacion_feedback.connect(self.actualizar_feedback_panel)
        self.hilo_vision.start()

    def refrescar_panel_gestos(self):
        while self.layout_gestos.count():
            child = self.layout_gestos.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        try:
            with open('config.json', 'r') as f:
                config_gestos = json.load(f)
            
            # Solo mostrar los primeros 4 gestos como sugeridos
            gestos_mostrados = 0
            for nombre_gesto, datos in config_gestos.items():
                if datos['accion'] != 'confirmacion' and gestos_mostrados < 4:
                    texto_gesto = f"▪ {nombre_gesto.replace('_', ' ').title()}"
                    desc_gesto = f"  └ {datos['descripcion']}"
                    label_gesto = QLabel(f"{texto_gesto}\n{desc_gesto}")
                    label_gesto.setStyleSheet("color: #333333; font-size: 14px;")
                    label_gesto.setWordWrap(True)
                    self.layout_gestos.addWidget(label_gesto)
                    gestos_mostrados += 1
        except Exception as e:
            self.layout_gestos.addWidget(QLabel(f"Error: {e}"))

    def abrir_dialogo_lista(self):
        try:
            with open('config.json', 'r') as f:
                config_gestos = json.load(f)
            dialogo = DialogoListaGestos(config_gestos, self)
            dialogo.exec()
        except Exception as e:
            print(f"Error al abrir la lista de gestos: {e}")

    def abrir_dialogo_modificar(self):
        try:
            with open('config.json', 'r') as f:
                config_gestos = json.load(f)
            
            acciones = list(ac.MAPA_ACCIONES.keys())
            
            dialogo = DialogoModificar(config_gestos, acciones, self)
            if dialogo.exec():
                nueva_config = dialogo.obtener_config_actualizada()
                with open('config.json', 'w') as f:
                    json.dump(nueva_config, f, indent=2)
                self.refrescar_panel_gestos()
            else:
                print("Modificación cancelada.")
        except Exception as e:
            print(f"Error al abrir el diálogo de modificación: {e}")

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
        pixmap_escalado = pixmap.scaled(self.etiqueta_video.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.etiqueta_video.setPixmap(pixmap_escalado)

    def closeEvent(self, event):
        self.hilo_vision.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())