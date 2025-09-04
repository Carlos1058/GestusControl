# Gestus Control: Controla tu PC con Gestos de Mano

Una aplicación de escritorio moderna que utiliza la cámara web para reconocer gestos de mano en tiempo real y ejecutar acciones personalizables en tu computadora, como abrir aplicaciones, controlar el volumen, el brillo y más.

## Acerca del Proyecto

Gestus Control nace de la idea de crear una forma más intuitiva y futurista de interactuar con nuestra computadora. Utilizando el poder de la visión por computadora, la aplicación traduce señas específicas en comandos del sistema, haciendo que tareas comunes sean más rápidas y accesibles.

### Características Principales

* **Reconocimiento en Tiempo Real:** Detección fluida de gestos a través de la webcam.
* **Flujo de Confirmación:** Un sistema de seguridad único que requiere un gesto de "LIKE" para ejecutar una acción, evitando comandos accidentales.
* **Alta Personalización:** Las acciones de cada gesto se pueden modificar fácilmente a través de una interfaz gráfica.
* **Control del Sistema:** Va más allá de abrir aplicaciones. Controla el volumen, el brillo de la pantalla, abre el menú de inicio y simula atajos de teclado.
* **Interfaz Moderna:** Un diseño limpio y fácil de entender, construido con PyQt6.

### Construido Con

* [Python](https://www.python.org/)
* [OpenCV](https://opencv.org/)
* [MediaPipe](https://mediapipe.dev/)
* [PyQt6](https://riverbankcomputing.com/software/pyqt/)
* [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)
* [Screen Brightness Control](https://github.com/Crozzers/screen_brightness_control)

## Empezando

Sigue estos pasos para obtener una copia local del proyecto y ponerla en funcionamiento.

### Prerrequisitos

Asegúrate de tener Python instalado en tu sistema. Se recomienda usar **Python 3.10** o **Python 3.11** para una máxima compatibilidad con las librerías del proyecto.
* [Descargar Python](https://www.python.org/downloads/)

### Instalación

1.  **Clona el repositorio** (o simplemente descarga los archivos en una carpeta). Si tienes Git, usa:
    ```sh
    git clone [https://github.com/tu_usuario/GestusControl.git](https://github.com/tu_usuario/GestusControl.git)
    cd GestusControl
    ```

2.  **(Opcional pero Muy Recomendado) Crea y activa un entorno virtual**

    Crear un entorno virtual es la mejor práctica para aislar las dependencias del proyecto y evitar conflictos con otros paquetes de tu sistema.

    * Desde la carpeta raíz del proyecto (`GestusControl`), ejecuta el siguiente comando. Reemplaza `3.10` con la versión de Python que instalaste si es diferente.
        ```sh
        py -3.10 -m venv venv
        ```
    * Activa el entorno virtual. Esto cambiará el prompt de tu terminal.
        * **En Windows (CMD/PowerShell):**
            ```sh
            .\venv\Scripts\activate
            ```
        * **En macOS/Linux:**
            ```sh
            source venv/bin/activate
            ```

3.  **Instala las dependencias**

    Con el entorno virtual activado, instala todos los paquetes necesarios usando el archivo `requirements.txt`.
    ```sh
    pip install -r requirements.txt
    ```

### Ejecución

Una vez que todas las dependencias estén instaladas, ejecuta la aplicación:
```sh
python app.py
