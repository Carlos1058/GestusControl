# reconocimiento_gestos.py

def identificar_gestos(mano_landmarks):
    """
    Analiza los puntos de una mano para identificar el gesto que está realizando.
    :param mano_landmarks: Los 21 puntos de la mano detectados por MediaPipe.
    :return: Una cadena de texto con el nombre del gesto detectado.
    """
    puntos = mano_landmarks.landmark

    # --- Lógica de Dedos Estirados/Cerrados (base para muchos gestos) ---
    # Un dedo está 'estirado' si la punta (Y) está por encima del nudillo medio (Y)
    indice_estirado = puntos[8].y < puntos[6].y
    medio_estirado = puntos[12].y < puntos[10].y
    anular_estirado = puntos[16].y < puntos[14].y
    menique_estirado = puntos[20].y < puntos[18].y
    
    # Un dedo está 'cerrado' si la punta (Y) está por debajo del nudillo inferior (Y)
    indice_cerrado = puntos[8].y > puntos[5].y
    medio_cerrado = puntos[12].y > puntos[9].y
    anular_cerrado = puntos[16].y > puntos[13].y
    menique_cerrado = puntos[20].y > puntos[17].y
    
    # Lógica del pulgar (es más complejo, depende del eje X y Y)
    pulgar_arriba = puntos[4].y < puntos[3].y and puntos[4].y < puntos[2].y
    pulgar_abajo = puntos[4].y > puntos[3].y and puntos[4].y > puntos[2].y
    pulgar_afuera = puntos[4].x < puntos[2].x if puntos[4].x < puntos[17].x else puntos[4].x > puntos[2].x


    # --- Evaluación de Gestos Específicos ---

    # Gesto LIKE (Pulgar arriba, resto cerrado)
    if pulgar_arriba and indice_cerrado and medio_cerrado and anular_cerrado and menique_cerrado:
        return "Like"

    # Gesto MANO_ABIERTA (Todos los dedos estirados)
    if indice_estirado and medio_estirado and anular_estirado and menique_estirado and pulgar_afuera:
        return "Mano abierta"

    # Gesto PUNO_CERRADO (Todos los dedos cerrados)
    if indice_cerrado and medio_cerrado and anular_cerrado and menique_cerrado and not pulgar_afuera:
        return "Puno cerrado"
        
    # Gesto PAZ (Índice y medio estirados, resto cerrado)
    if indice_estirado and medio_estirado and anular_cerrado and menique_cerrado:
        return "Paz"

    # Gesto CUERNOS (Índice y meñique estirados, resto cerrado)
    if indice_estirado and menique_estirado and medio_cerrado and anular_cerrado:
        return "Cuernos"

    # Gesto LLAMAME (Pulgar y meñique estirados, resto cerrado)
    if pulgar_afuera and menique_estirado and indice_cerrado and medio_cerrado and anular_cerrado:
        return "Llamame"

    # Gesto PULGAR_ABAJO (Pulgar abajo, resto cerrado)
    if pulgar_abajo and indice_cerrado and medio_cerrado and anular_cerrado and menique_cerrado:
        return "Pulgar abajo"

    # Gesto OK (Punta del índice y pulgar se tocan, resto estirado)
    # (Calculamos la distancia entre las puntas de los dedos)
    distancia_ok = ((puntos[8].x - puntos[4].x)**2 + (puntos[8].y - puntos[4].y)**2)**0.5
    if distancia_ok < 0.05 and medio_estirado and anular_estirado and menique_estirado:
        return "Ok"

    # Gesto CRUZADO (Dedos índice y medio cruzados)
    if indice_estirado and medio_estirado and anular_cerrado and menique_cerrado:
        # Distancia entre puntas muy pequeña
        distancia_cruz = abs(puntos[8].x - puntos[12].x)
        if distancia_cruz < 0.04: 
             return "Cruzado"

    # Gesto INDICE ARRIBA (Solo índice estirado, pulgar cerrado)
    if indice_estirado and medio_cerrado and anular_cerrado and menique_cerrado and not pulgar_afuera:
        return "Indice Arriba"

    # Si no se cumple ninguna condición
    return "Desconocido"