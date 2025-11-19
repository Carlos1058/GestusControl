from PyQt6.QtCore import QThread, pyqtSignal
import cv2, mediapipe as mp, time, json
import reconocimiento_gestos as rg, acciones as ac

class MotorVision(QThread):
    cambio_de_frame = pyqtSignal(object)
    actualizacion_feedback = pyqtSignal(str, str, str)
    
    # Nuevas señales para el Overlay
    gesto_progreso = pyqtSignal(float)      # 0.0 a 1.0
    gesto_confirmado_signal = pyqtSignal(str) # Nombre del gesto confirmado
    gesto_cancelado_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config_gestos = json.load(f)
        except Exception:
            self.config_gestos = {"acciones": [], "gestos": []}
        self.mp_manos = mp.solutions.hands
        self.manos = self.mp_manos.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_dibujo = mp.solutions.drawing_utils
        
        # Variables de estado
        self.gesto_actual_persistente = "Desconocido"
        self.tiempo_inicio_gesto = 0
        self.TIEMPO_PARA_CONFIRMAR = 1.5 # Segundos para confirmar manteniendo
        self.accion_ejecutada = False

    def run(self):
        cap = cv2.VideoCapture(0)
        feedback_anterior = ("", "", "")

        while self.running and cap.isOpened():
            exito, frame = cap.read()
            if not exito: continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = self.manos.process(frame_rgb)
            
            gesto_detectado_ahora = "Desconocido"
            
            if resultados.multi_hand_landmarks:
                for mano_landmarks in resultados.multi_hand_landmarks:
                    self.mp_dibujo.draw_landmarks(frame, mano_landmarks, self.mp_manos.HAND_CONNECTIONS)
                    gesto_detectado_ahora = rg.identificar_gestos(mano_landmarks)
            
            # --- Lógica de Hold-to-Confirm ---
            
            # Si detectamos un gesto válido (que está en la config)
            es_gesto_valido = any(g["nombre"] == gesto_detectado_ahora for g in self.config_gestos["gestos"])
            
            if es_gesto_valido:
                if gesto_detectado_ahora != self.gesto_actual_persistente:
                    # Nuevo gesto detectado (o cambio de gesto)
                    self.gesto_actual_persistente = gesto_detectado_ahora
                    self.tiempo_inicio_gesto = time.time()
                    self.accion_ejecutada = False
                    self.gesto_progreso.emit(0.0)
                else:
                    # Mismo gesto manteniéndose
                    if not self.accion_ejecutada:
                        tiempo_transcurrido = time.time() - self.tiempo_inicio_gesto
                        progreso = min(1.0, tiempo_transcurrido / self.TIEMPO_PARA_CONFIRMAR)
                        
                        self.gesto_progreso.emit(progreso)
                        
                        if tiempo_transcurrido >= self.TIEMPO_PARA_CONFIRMAR:
                            # CONFIRMACIÓN
                            self.accion_ejecutada = True
                            self.gesto_confirmado_signal.emit(self.gesto_actual_persistente)
                            self.ejecutar_accion(self.gesto_actual_persistente)
            else:
                # No hay gesto o es desconocido
                if self.gesto_actual_persistente != "Desconocido":
                    # Se perdió el gesto
                    self.gesto_actual_persistente = "Desconocido"
                    self.gesto_cancelado_signal.emit()
                    self.accion_ejecutada = False

            self.cambio_de_frame.emit(frame)
            
            # Feedback de texto para el panel lateral (opcional, pero útil)
            estado_texto = "Confirmado" if self.accion_ejecutada else ("Detectando..." if es_gesto_valido else "Esperando")
            
            # Calcular el progreso solo si es_gesto_valido y no se ha ejecutado la acción
            progreso_texto = ""
            if es_gesto_valido and not self.accion_ejecutada:
                tiempo_transcurrido = time.time() - self.tiempo_inicio_gesto
                progreso_porcentaje = int(min(1.0, tiempo_transcurrido / self.TIEMPO_PARA_CONFIRMAR) * 100)
                progreso_texto = f"Progreso: {progreso_porcentaje}%"
            else:
                progreso_texto = "Progreso: 0%" # O dejar vacío si no se quiere mostrar nada
            
            feedback_actual = (estado_texto, gesto_detectado_ahora, progreso_texto)
            
            if feedback_actual != feedback_anterior:
                self.actualizacion_feedback.emit(*feedback_actual)
                feedback_anterior = feedback_actual
            
            time.sleep(0.01)
        cap.release()

    def ejecutar_accion(self, nombre_gesto):
        # Buscar ID de acción
        id_accion = next((g["accion"] for g in self.config_gestos["gestos"] if g["nombre"] == nombre_gesto), None)
        if id_accion is not None: # Asegurarse de que id_accion no sea None
            if id_accion < len(self.config_gestos["acciones"]): # Prevenir IndexError
                nombre_accion_sistema = self.config_gestos["acciones"][id_accion]["nombre"]
                if nombre_accion_sistema in ac.MAPA_ACCIONES:
                    print(f"Ejecutando: {nombre_accion_sistema}")
                    ac.MAPA_ACCIONES[nombre_accion_sistema]()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()