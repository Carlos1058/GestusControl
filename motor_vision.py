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
    
    # Señal para Dwell Click
    dwell_progreso = pyqtSignal(float, int, int) # Progreso (0-1), X, Y

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
        self.scroll_detectado = False
        self.prev_scroll_y = 0
        
        # Variables Dwell Click
        self.tiempo_inicio_dwell = 0
        self.prev_x_dwell, self.prev_y_dwell = 0, 0
        self.TIEMPO_DWELL = 1.5 # Segundos para click

    def toggle_modo_mouse(self):
        self.modo_mouse = not self.modo_mouse
        # Limpiar estado de dwell al cambiar de modo
        self.tiempo_inicio_dwell = 0
        self.dwell_progreso.emit(0.0, 0, 0)
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
                        # --- LÓGICA MODO MOUSE + SCROLL ---
                        h_frame, w_frame, _ = frame.shape
                        
                        # Detectar dedos levantados (Índice y Medio)
                        dedo_indice_arriba = mano_landmarks.landmark[8].y < mano_landmarks.landmark[6].y
                        dedo_medio_arriba = mano_landmarks.landmark[12].y < mano_landmarks.landmark[10].y
                        dedo_anular_abajo = mano_landmarks.landmark[16].y > mano_landmarks.landmark[14].y
                        dedo_menique_abajo = mano_landmarks.landmark[20].y > mano_landmarks.landmark[18].y
                        
                        es_gesto_scroll = dedo_indice_arriba and dedo_medio_arriba and dedo_anular_abajo and dedo_menique_abajo
                        
                        # 1. Obtener posición media de los dedos activos
                        x_indice = mano_landmarks.landmark[8].x
                        y_indice = mano_landmarks.landmark[8].y
                        
                        if es_gesto_scroll:
                            # --- MODO SCROLL ---
                            if not self.scroll_detectado:
                                self.prev_scroll_y = y_indice
                                self.scroll_detectado = True
                            
                            # Calcular desplazamiento vertical
                            dy = self.prev_scroll_y - y_indice # Invertido: mover mano arriba = scroll arriba
                            
                            # Aplicar Scroll (ajustar sensibilidad)
                            sensibilidad_scroll = 1500 
                            if abs(dy) > 0.01: # Zona muerta
                                pyautogui.scroll(int(dy * sensibilidad_scroll))
                                
                            self.prev_scroll_y = y_indice
                            gesto_detectado_ahora = "Modo Scroll"
                            # No movemos el mouse en modo scroll para evitar caos
                            
                            # Resetear dwell si hacemos scroll
                            self.tiempo_inicio_dwell = 0
                            self.dwell_progreso.emit(0.0, 0, 0)
                            
                        else:
                            # --- MODO MOUSE (Un solo dedo o Click) ---
                            self.scroll_detectado = False
                            
                            # 2. Mapeo de Coordenadas (con margen)
                            margen = 0.15 
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
                            
                            # 4. Detección de Dwell Click (Permanencia con Ancla)
                            # Si no estamos en dwell, iniciamos
                            if self.tiempo_inicio_dwell == 0:
                                self.tiempo_inicio_dwell = time.time()
                                self.prev_x_dwell, self.prev_y_dwell = curr_x, curr_y # Usamos prev_x_dwell como ANCLA
                                
                            # Calcular distancia desde el ANCLA (no desde el frame anterior)
                            distancia_ancla = ((curr_x - self.prev_x_dwell)**2 + (curr_y - self.prev_y_dwell)**2)**0.5
                            
                            RADIO_TOLERANCIA = 40 # Píxeles de tolerancia para temblores
                            
                            if distancia_ancla < RADIO_TOLERANCIA:
                                # Estamos dentro del radio, continuar dwell
                                tiempo_dwell = time.time() - self.tiempo_inicio_dwell
                                self.tiempo_inicio_dwell = 0
                                self.click_detectado = False
                                self.dwell_progreso.emit(0.0, int(curr_x), int(curr_y))
                                # El nuevo ancla se establecerá en el siguiente frame al entrar en el if inicial
                                
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

            # --- DIBUJAR HUD CYBERPUNK ---
            self.dibujar_hud(frame)

            self.cambio_de_frame.emit(frame)
            
            # Feedback de texto
            if self.modo_mouse:
                estado_texto = "Activo"
                if self.scroll_detectado:
                    progreso_texto = "SCROLL"
                else:
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

    def dibujar_hud(self, frame):
        """Dibuja elementos gráficos tácticos sobre el frame."""
        h, w, _ = frame.shape
        color_hud = (255, 229, 0) # Cyan en BGR (0, 229, 255)
        
        grosor = 2
        longitud = 40

        # 1. Esquinas (Brackets)
        # Arriba-Izquierda
        cv2.line(frame, (20, 20), (20 + longitud, 20), color_hud, grosor)
        cv2.line(frame, (20, 20), (20, 20 + longitud), color_hud, grosor)
        
        # Arriba-Derecha
        cv2.line(frame, (w - 20, 20), (w - 20 - longitud, 20), color_hud, grosor)
        cv2.line(frame, (w - 20, 20), (w - 20, 20 + longitud), color_hud, grosor)
        
        # Abajo-Izquierda
        cv2.line(frame, (20, h - 20), (20 + longitud, h - 20), color_hud, grosor)
        cv2.line(frame, (20, h - 20), (20, h - 20 - longitud), color_hud, grosor)
        
        # Abajo-Derecha
        cv2.line(frame, (w - 20, h - 20), (w - 20 - longitud, h - 20), color_hud, grosor)
        cv2.line(frame, (w - 20, h - 20), (w - 20, h - 20 - longitud), color_hud, grosor)

        # 2. Retícula Central
        cx, cy = w // 2, h // 2
        cv2.line(frame, (cx - 10, cy), (cx + 10, cy), color_hud, 1)
        cv2.line(frame, (cx, cy - 10), (cx, cy + 10), color_hud, 1)
        cv2.circle(frame, (cx, cy), 20, color_hud, 1)

        # 3. Texto de Estado
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "SYS: ONLINE", (40, 50), font, 0.5, color_hud, 1, cv2.LINE_AA)
        cv2.putText(frame, "CAM: ACTIVE", (40, 70), font, 0.5, color_hud, 1, cv2.LINE_AA)
        
        # Modo Mouse indicador en video
        if self.modo_mouse:
            cv2.putText(frame, "MOUSE MODE: ON", (w - 180, 50), font, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

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