# acciones.py

import webbrowser
import subprocess
import pyautogui         # Nueva librería para controlar teclado y mouse
import screen_brightness_control as sbc # Nueva librería para el brillo

# --- Acciones del Navegador y Sistema ---

def abrir_youtube():
    """Abre youtube.com en el navegador predeterminado."""
    print("ACCIÓN: Abriendo YouTube...")
    webbrowser.open("https://www.youtube.com")

def abrir_calculadora():
    """Abre la calculadora del sistema."""
    print("ACCIÓN: Abriendo la Calculadora...")
    try:
        subprocess.run(["calc.exe"])
    except FileNotFoundError:
        try:
            subprocess.run(["gnome-calculator"])
        except FileNotFoundError:
            print("No se encontró la calculadora.")

def abrir_wikipedia():
    """Abre wikipedia.org en el navegador."""
    print("ACCIÓN: Abriendo Wikipedia...")
    webbrowser.open("https://www.wikipedia.org")


# --- Nuevas Acciones de Control del Sistema ---

def abrir_menu_inicio():
    """Simula la pulsación de la tecla de Windows para abrir el menú de inicio."""
    print("ACCIÓN: Abriendo Menú Inicio...")
    pyautogui.press('win')

def activar_cortana():
    """Simula la pulsación de Windows + C para activar Cortana/Copilot."""
    print("ACCIÓN: Activando Cortana/Copilot...")
    pyautogui.hotkey('win', 'c')

def subir_brillo():
    """Sube el brillo de la pantalla principal en 20 puntos."""
    print("ACCIÓN: Subiendo brillo...")
    try:
        sbc.set_brightness('+20')
    except Exception as e:
        print(f"No se pudo ajustar el brillo: {e}")

def bajar_brillo():
    """Baja el brillo de la pantalla principal en 20 puntos."""
    print("ACCIÓN: Bajando brillo...")
    try:
        sbc.set_brightness('-20')
    except Exception as e:
        print(f"No se pudo ajustar el brillo: {e}")

def subir_volumen():
    """Sube el volumen del sistema."""
    print("ACCIÓN: Subiendo volumen...")
    pyautogui.press('volumeup')

def bajar_volumen():
    """Baja el volumen del sistema."""
    print("ACCIÓN: Bajando volumen...")
    pyautogui.press('volumedown')

def silenciar_volumen():
    """Silencia/activa el sonido del sistema."""
    print("ACCIÓN: Silenciando volumen...")
    pyautogui.press('volumemute')

def siguiente_cancion():
    """Salta a la siguiente canción en reproductores multimedia."""
    print("ACCIÓN: Siguiente Canción...")
    pyautogui.press('nexttrack')

def pausar_musica():
    """Pausa o reproduce multimedia."""
    print("ACCIÓN: Pausar/Reproducir...")
    pyautogui.press('playpause')

def cambiar_pestana():
    """Alterna entre pestañas (Ctrl + Tab)."""
    print("ACCIÓN: Cambiando Pestaña...")
    pyautogui.hotkey('ctrl', 'tab')



# --- Mapa de Acciones Actualizado ---
# Este diccionario conecta los strings del JSON con las funciones reales.

MAPA_ACCIONES = {
    "Abrir YouTube": abrir_youtube,
    "Abrir calculadora": abrir_calculadora,
    "Abrir Wikipedia": abrir_wikipedia,
    "Abrir menu de inicio": abrir_menu_inicio,
    "Activar Cortana": activar_cortana,
    "Subir brillo": subir_brillo,
    "Bajar brillo": bajar_brillo,
    "Subir volumen": subir_volumen,
    "Bajar volumen": bajar_volumen,
    "Silenciar volumen": silenciar_volumen,
    "Siguiente Cancion": siguiente_cancion,
    "Pausar/Reproducir": pausar_musica,
    "Cambiar Pestana": cambiar_pestana,
}
