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


# --- Mapa de Acciones Actualizado ---
# Este diccionario conecta los strings del JSON con las funciones reales.

MAPA_ACCIONES = {
    "abrir_youtube": abrir_youtube,
    "abrir_calculadora": abrir_calculadora,
    "abrir_wikipedia": abrir_wikipedia,
    "abrir_menu_inicio": abrir_menu_inicio,
    "activar_cortana": activar_cortana,
    "subir_brillo": subir_brillo,
    "bajar_brillo": bajar_brillo,
    "subir_volumen": subir_volumen,
    "bajar_volumen": bajar_volumen,
    "silenciar_volumen": silenciar_volumen,
}