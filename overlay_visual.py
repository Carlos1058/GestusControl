from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
import sys

class OverlayVisual(QWidget):
    def __init__(self):
        super().__init__()
        # Configuración de ventana transparente y "click-through"
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |  # No aparece en la barra de tareas
            Qt.WindowType.WindowTransparentForInput  # Click-through
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Ocupar toda la pantalla
        self.showFullScreen()
        
        # Estado
        self._color_borde = QColor(0, 0, 0, 0)  # Invisible por defecto
        self._grosor = 0
        self.progreso = 0.0 # 0.0 a 1.0
        
        # Estado Dwell Click
        self.dwell_active = False
        self.dwell_x = 0
        self.dwell_y = 0
        self.dwell_progreso = 0.0
        
        # Animación de pulsación (opcional, por ahora controlada por progreso)
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.update)
        self.timer_animacion.start(30) # 30ms refresh rate
        
        # Forzar que la ventana se mantenga arriba
        self.timer_top = QTimer(self)
        self.timer_top.timeout.connect(self.mantener_encima)
        self.timer_top.start(1000) # Cada 1 segundo

    def mantener_encima(self):
        self.raise_()

    def set_estado(self, estado, progreso=0.0):
        """
        Actualiza el aspecto visual según el estado del gesto.
        estado: "Detectando", "Confirmado", "Cancelado", "Inactivo"
        progreso: float de 0.0 a 1.0
        """
        self.progreso = max(0.0, min(1.0, progreso))
        
        if estado == "Detectando":
            # Color Amarillo/Azul que se intensifica
            alpha = int(100 + (155 * self.progreso)) # 100 a 255
            # Interpolación de color: Amarillo a Naranja
            self._color_borde = QColor(255, 215, 0, alpha) 
            self._grosor = 10 + (20 * self.progreso) # Engrosa el borde
            
        elif estado == "Confirmado":
            # Flash Verde
            self._color_borde = QColor(0, 255, 0, 200)
            self._grosor = 40
            # Timer para desaparecer después del flash
            QTimer.singleShot(500, lambda: self.set_estado("Inactivo"))
            
        elif estado == "Cancelado":
            # Rojo desvaneciéndose
            self._color_borde = QColor(255, 0, 0, 150)
            self._grosor = 10
            QTimer.singleShot(300, lambda: self.set_estado("Inactivo"))
            
        elif estado == "Inactivo":
            self._color_borde = QColor(0, 0, 0, 0)
            self._grosor = 0
            self.progreso = 0.0
            
        # Seguridad: Si estamos mostrando estado de gestos, desactivar dwell
        if estado != "Modo Mouse": # Asumiendo que "Modo Mouse" no usa set_estado
            self.dwell_active = False
            
        self.update()

    def set_dwell_estado(self, progreso, x, y):
        """Actualiza el estado del Dwell Click (círculo de carga)."""
        self.dwell_progreso = max(0.0, min(1.0, progreso))
        self.dwell_x = x
        self.dwell_y = y
        self.dwell_active = self.dwell_progreso > 0
        self.update()

    def set_progreso_gesto(self, progreso):
        """Actualiza el progreso del gesto actual (0.0 a 1.0)."""
        self.set_estado("Detectando", progreso)

    def reset_progreso(self):
        """Reinicia el estado visual."""
        self.set_estado("Inactivo")

    def mostrar_confirmacion(self, nombre_gesto):
        """Muestra un feedback visual de confirmación."""
        self.set_estado("Confirmado")
        # Aquí podríamos dibujar el nombre del gesto en el centro si quisiéramos
        self.mensaje_centro = nombre_gesto
        self.tiempo_mensaje = 150 # frames
        self.update()

    def mostrar_mensaje_centro(self, mensaje):
        """Muestra un mensaje temporal en el centro."""
        self.mensaje_centro = mensaje
        self.tiempo_mensaje = 150
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Dibujar Borde de Estado (Glow)
        if self._grosor > 0:
            pen = QPen(self._color_borde)
            pen.setWidth(int(self._grosor))
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            rect = self.rect().adjusted(10, 10, -10, -10)
            painter.drawRoundedRect(rect, 20, 20)

        # 2. Dibujar Dwell Click (Círculo de carga)
        if self.dwell_active:
            color_dwell = QColor(0, 229, 255) # Cyan
            radio = 30
            pen_base = QPen(QColor(0, 229, 255, 50))
            pen_base.setWidth(4)
            painter.setPen(pen_base)
            painter.drawEllipse(self.dwell_x - radio, self.dwell_y - radio, radio * 2, radio * 2)
            
            pen_progreso = QPen(color_dwell)
            pen_progreso.setWidth(4)
            pen_progreso.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_progreso)
            angulo_span = int(360 * 16 * self.dwell_progreso)
            painter.drawArc(self.dwell_x - radio, self.dwell_y - radio, radio * 2, radio * 2, 90 * 16, -angulo_span)


        # 3. Dibujar Mensaje Central (si existe)
        if hasattr(self, 'mensaje_centro') and self.mensaje_centro and getattr(self, 'tiempo_mensaje', 0) > 0:
            self.tiempo_mensaje -= 1
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.mensaje_centro)
            if self.tiempo_mensaje <= 0:
                self.mensaje_centro = ""
                self.update()
            else:
                self.update() # Seguir animando

        # 4. Dibujar Tutorial (Instrucciones)
        if hasattr(self, 'tutorial_titulo') and self.tutorial_titulo:
            # Fondo semitransparente para legibilidad
            bg_rect = self.rect()
            # Un overlay oscuro sutil
            painter.fillRect(bg_rect, QColor(0, 0, 0, 100))
            
            # Titulo
            painter.setPen(QColor(0, 229, 255)) # Cyan
            font_title = painter.font()
            font_title.setPointSize(32)
            font_title.setBold(True)
            painter.setFont(font_title)
            
            # Posición superior
            rect_titulo = self.rect().adjusted(0, 100, 0, 0)
            painter.drawText(rect_titulo, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.tutorial_titulo)
            
            # Instrucción
            if hasattr(self, 'tutorial_instruccion') and self.tutorial_instruccion:
                painter.setPen(QColor(255, 255, 255))
                font_inst = painter.font()
                font_inst.setPointSize(18)
                painter.setFont(font_inst)
                
                rect_inst = self.rect().adjusted(0, 160, 0, 0)
                painter.drawText(rect_inst, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.tutorial_instruccion)

    def set_tutorial_info(self, titulo, instruccion):
        """Muestra información del tutorial en pantalla."""
        self.tutorial_titulo = titulo
        self.tutorial_instruccion = instruccion
        self.update()


if __name__ == "__main__":
    # Test rápido
    app = QApplication(sys.argv)
    overlay = OverlayVisual()
    overlay.show()
    
    # Simulación de ciclo
    def simular_gesto():
        # 0-100: Detectando
        # 100-105: Confirmado
        # 105-120: Inactivo
        t = 0
        timer = QTimer()
        def paso():
            nonlocal t
            t += 1
            if t < 50:
                overlay.set_estado("Detectando", t/50)
            elif t == 50:
                overlay.set_estado("Confirmado")
            elif t > 60:
                timer.stop()
                app.quit()
        
        timer.timeout.connect(paso)
        timer.start(50)
        
    QTimer.singleShot(1000, simular_gesto)
    sys.exit(app.exec())
