from PyQt6.QtCore import QThread, pyqtSignal
import cv2, mediapipe as mp, time, json
import pyautogui
pyautogui.PAUSE = 0 # Eliminar delay por defecto de PyAutoGUI
pyautogui.FAILSAFE = False # Evitar excepciones si se toca la esquina
import numpy as np
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
        
        # --- Variables Modo Mouse ---
        self.modo_mouse = False
        self.pantalla_w, self.pantalla_h = pyautogui.size()
        self.prev_x, self.prev_y = 0, 0
        self.suavizado = 2 # Reducido de 5 a 2 para menos lag
        self.click_detectado = False

    def toggle_modo_mouse(self):
        self.modo_mouse = not self.modo_mouse
        return self.modo_mouse

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
            es_gesto_valido = False
            
            if resultados.multi_hand_landmarks:
                for mano_landmarks in resultados.multi_hand_landmarks:
                    self.mp_dibujo.draw_landmarks(frame, mano_landmarks, self.mp_manos.HAND_CONNECTIONS)
                    
                    if self.modo_mouse:
                        # --- LÓGICA MODO MOUSE ---
                        h_frame, w_frame, _ = frame.shape
                        
                        # 1. Obtener punta del índice (8)
                        x_indice = mano_landmarks.landmark[8].x
                        y_indice = mano_landmarks.landmark[8].y
                        
                        # 2. Mapeo de Coordenadas (con margen)
                        margen = 0.15 # 15% de margen
                        x_interp = np.interp(x_indice, [margen, 1-margen], [0, self.pantalla_w])
                        y_interp = np.interp(y_indice, [margen, 1-margen], [0, self.pantalla_h])
                        
                        # 3. Suavizado
                        curr_x = self.prev_x + (x_interp - self.prev_x) / self.suavizado
                        curr_y = self.prev_y + (y_interp - self.prev_y) / self.suavizado
                        
                        # Mover mouse
                        try:
                            pyautogui.moveTo(curr_x, curr_y)
                        except pyautogui.FailSafeException:
                            pass
                            
                        self.prev_x, self.prev_y = curr_x, curr_y
                        
                        # 4. Detección de Click (Distancia Índice 8 - Pulgar 4)
                        x_pulgar = mano_landmarks.landmark[4].x
                        y_pulgar = mano_landmarks.landmark[4].y
                        
                        distancia = ((x_indice - x_pulgar)**2 + (y_indice - y_pulgar)**2)**0.5
                        
                        if distancia < 0.05: # Umbral de click
                            if not self.click_detectado:
                                pyautogui.click()
                                self.click_detectado = True
                        else:
                            self.click_detectado = False
                            
                        gesto_detectado_ahora = "Modo Mouse"
                        
                    else:
                        # --- LÓGICA GESTOS NORMAL ---
                        gesto_detectado_ahora = rg.identificar_gestos(mano_landmarks)
            
            # --- Lógica de Hold-to-Confirm (Solo si NO es modo mouse) ---
            if not self.modo_mouse:
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
            else:
                # En modo mouse, siempre "confirmamos" visualmente que está activo
                es_gesto_valido = True 

            self.cambio_de_frame.emit(frame)
            
            # Feedback de texto
            if self.modo_mouse:
                estado_texto = "Activo"
                progreso_texto = "Click: " + ("SI" if self.click_detectado else "NO")
            else:
                estado_texto = "Confirmado" if self.accion_ejecutada else ("Detectando..." if es_gesto_valido else "Esperando")
                progreso_texto = ""
                if es_gesto_valido and not self.accion_ejecutada:
                    tiempo_transcurrido = time.time() - self.tiempo_inicio_gesto
                    progreso_porcentaje = int(min(1.0, tiempo_transcurrido / self.TIEMPO_PARA_CONFIRMAR) * 100)
                    progreso_texto = f"Progreso: {progreso_porcentaje}%"
                else:
                    progreso_texto = "Progreso: 0%"
            
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