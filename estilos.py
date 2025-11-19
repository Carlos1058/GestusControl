# estilos.py

# Paleta de Colores
COLOR_FONDO = "#121212"
COLOR_PANEL = "#1E1E1E"
COLOR_TEXTO = "#FFFFFF"
COLOR_TEXTO_SECUNDARIO = "#B0B0B0"
COLOR_ACENTO_CYAN = "#00E5FF"
COLOR_ACENTO_MAGENTA = "#D500F9"
COLOR_BORDE = "#333333"

HOJA_ESTILO = f"""
    QMainWindow, QDialog {{
        background-color: {COLOR_FONDO};
        color: {COLOR_TEXTO};
    }}

    QWidget {{
        color: {COLOR_TEXTO};
        font-family: "Segoe UI", sans-serif;
        font-size: 14px;
    }}

    /* --- Paneles y Contenedores --- */
    QFrame, QWidget#PanelDerecho {{
        background-color: {COLOR_PANEL};
        border: 1px solid {COLOR_BORDE};
        border-radius: 8px;
    }}

    /* --- Etiquetas (Labels) --- */
    QLabel {{
        color: {COLOR_TEXTO};
        border: none;
    }}
    
    QLabel#Titulo {{
        font-size: 22px;
        font-weight: bold;
        color: {COLOR_ACENTO_CYAN};
        margin-bottom: 10px;
    }}

    QLabel#Subtitulo {{
        font-size: 18px;
        font-weight: bold;
        color: {COLOR_TEXTO_SECUNDARIO};
        margin-top: 10px;
    }}
    
    QLabel#InfoTexto {{
        font-size: 16px;
        color: {COLOR_TEXTO};
        padding: 2px;
    }}

    /* --- Botones Generales --- */
    QPushButton {{
        background-color: {COLOR_PANEL};
        color: {COLOR_ACENTO_CYAN};
        border: 2px solid {COLOR_ACENTO_CYAN};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
    }}

    QPushButton:hover {{
        background-color: {COLOR_ACENTO_CYAN};
        color: {COLOR_FONDO};
    }}

    QPushButton:pressed {{
        background-color: #00B8D4; /* Cyan un poco más oscuro */
        border-color: #00B8D4;
    }}

    /* --- Botón de Acción Principal (Iniciar/Parar) --- */
    QPushButton#BotonAccion {{
        background-color: {COLOR_ACENTO_MAGENTA};
        color: white;
        border: none;
        font-size: 16px;
        padding: 12px;
    }}

    QPushButton#BotonAccion:hover {{
        background-color: #AA00FF;
    }}

    /* --- Listas y Tablas --- */
    QListWidget, QTableWidget {{
        background-color: {COLOR_PANEL};
        border: 1px solid {COLOR_BORDE};
        border-radius: 4px;
        color: {COLOR_TEXTO};
        gridline-color: {COLOR_BORDE};
    }}

    QHeaderView::section {{
        background-color: {COLOR_FONDO};
        color: {COLOR_TEXTO};
        padding: 4px;
        border: 1px solid {COLOR_BORDE};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLOR_ACENTO_CYAN};
        color: {COLOR_FONDO};
    }}
"""
