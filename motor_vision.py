from PyQt6.QtCore import QThread, pyqtSignal
import cv2, mediapipe as mp, time, json
import reconocimiento_gestos as rg, acciones as ac

class MotorVision(QThread):
    cambio_de_frame = pyqtSignal(object)
    actualizacion_feedback = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        try:
            with open('config.json', 'r') as f:
                self.config_gestos = json.load(f)
        except Exception:
            self.config_gestos = {"acciones": [], "gestos": []}
        self.mp_manos = mp.solutions.hands
        self.manos = self.mp_manos.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_dibujo = mp.solutions.drawing_utils
        self.estado_actual = "Esperando gesto"
        self.gesto_anterior = ""
        self.tiempo_inicio_gesto = 0
        self.gesto_confirmado = ""
        self.accion_pendiente = None
        self.tiempo_inicio_confirmacion = 0
        self.TIEMPO_PARA_CONFIRMAR = 1.5
        self.TIEMPO_LIMITE_CONFIRMACION = 5

    def run(self):
        cap = cv2.VideoCapture(0)
        # ## NUEVO: Variables para controlar cuándo emitir la señal ##
        feedback_anterior = ("", "", "")

        while self.running and cap.isOpened():
            exito, frame = cap.read()
            if not exito: continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = self.manos.process(frame_rgb)
            gesto_actual = "Desconocido"
            texto_feedback = ""
            
            if resultados.multi_hand_landmarks:
                for mano_landmarks in resultados.multi_hand_landmarks:
                    self.mp_dibujo.draw_landmarks(frame, mano_landmarks, self.mp_manos.HAND_CONNECTIONS)
                    gesto_actual = rg.identificar_gestos(mano_landmarks)
                    if gesto_actual != self.gesto_anterior:
                        self.gesto_anterior = gesto_actual
                        self.tiempo_inicio_gesto = time.time()
                        self.gesto_confirmado = ""
                    elif gesto_actual != "Desconocido":
                        if (time.time() - self.tiempo_inicio_gesto) >= self.TIEMPO_PARA_CONFIRMAR:
                            self.gesto_confirmado = gesto_actual
            
            if self.estado_actual == "Esperando gesto":
                texto_feedback = "Muestre un gesto para iniciar."
                if self.gesto_confirmado and self.gesto_confirmado in {gesto["nombre"] for gesto in self.config_gestos["gestos"]}:
                    id_accion = next((gesto["accion"] for gesto in self.config_gestos["gestos"] if gesto["nombre"] == self.gesto_confirmado), None)
                    nombre_accion = self.config_gestos["acciones"][id_accion]["nombre"]
                    if nombre_accion != "Confirmar" and nombre_accion in ac.MAPA_ACCIONES:
                        self.accion_pendiente = ac.MAPA_ACCIONES[nombre_accion]
                        self.estado_actual = "Esperando confirmación"
                        self.tiempo_inicio_confirmacion = time.time()
                        self.gesto_confirmado, self.gesto_anterior = "", ""
            
            elif self.estado_actual == "Esperando confirmación":
                if not self.accion_pendiente:
                    nombre_accion = ""
                texto_feedback = f"Accion: {nombre_accion}. Confirme con Like."
                if time.time() - self.tiempo_inicio_confirmacion > self.TIEMPO_LIMITE_CONFIRMACION:
                    self.estado_actual, self.accion_pendiente = "Esperando gesto", None
                if self.gesto_confirmado == "Like":
                    if self.accion_pendiente: self.accion_pendiente()
                    self.estado_actual, self.accion_pendiente = "Esperando gesto", None
                    self.gesto_confirmado, self.gesto_anterior = "", ""

            self.cambio_de_frame.emit(frame)
            
            # ## MODIFICADO: Solo emitimos si la información ha cambiado ##
            feedback_actual = (self.estado_actual, gesto_actual, texto_feedback)
            if feedback_actual != feedback_anterior:
                self.actualizacion_feedback.emit(*feedback_actual)
                feedback_anterior = feedback_actual
            
            time.sleep(0.01)
        cap.release()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()