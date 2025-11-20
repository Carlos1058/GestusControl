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

    def paintEvent(self, event):
        if self._grosor <= 0 and not self.dwell_active: # Modificado para permitir pintar si solo dwell está activo
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dibujar borde
        pen = QPen(self._color_borde)
        pen.setWidth(int(self._grosor))
        # Alineación del borde: Inset para que no se corte
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        rect = self.rect().adjusted(
            int(self._grosor/2), int(self._grosor/2), 
            -int(self._grosor/2), -int(self._grosor/2)
        )
        painter.drawRect(rect)
        
        # Dibujar Dwell Click (Círculo de carga)
        if self.dwell_active:
            # Configuración estilo Cyberpunk
            color_dwell = QColor(0, 229, 255) # Cyan
            radio = 30
            
            # 1. Círculo base (fondo tenue)
            pen_base = QPen(QColor(0, 229, 255, 50))
            pen_base.setWidth(4)
            painter.setPen(pen_base)
            painter.drawEllipse(self.dwell_x - radio, self.dwell_y - radio, radio * 2, radio * 2)
            
            # 2. Arco de progreso
            pen_progreso = QPen(color_dwell)
            pen_progreso.setWidth(4)
            pen_progreso.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_progreso)
            
            angulo_span = int(360 * 16 * self.dwell_progreso) # 16 es para convertir a 1/16 de grado
            # drawArc toma: x, y, w, h, startAngle, spanAngle
            # startAngle 90 grados (12 en punto) = 90 * 16 = 1440
            painter.drawArc(self.dwell_x - radio, self.dwell_y - radio, radio * 2, radio * 2, 90 * 16, -angulo_span)

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
