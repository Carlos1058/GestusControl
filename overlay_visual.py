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
        
        # Animación de pulsación (opcional, por ahora controlada por progreso)
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.update)
        self.timer_animacion.start(30) # 30ms refresh rate

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
            
        self.update()

    def paintEvent(self, event):
        if self._grosor <= 0 or self._color_borde.alpha() == 0:
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
