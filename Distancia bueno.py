import cv2
import numpy as np
import math

# Dimensiones reales del área seleccionada (en mm)
AREA_ANCHO_MM = 247.0
AREA_ALTO_MM = 184.0

def seleccionar_area_de_trabajo(frame):
    """
    Permite al usuario seleccionar manualmente un área de trabajo.
    Devuelve las coordenadas de la región seleccionada (x, y, w, h).
    """
    roi = cv2.selectROI("Seleccione el área de trabajo", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Seleccione el área de trabajo")
    return roi

def convertir_px_a_mm(x_px, y_px, area_ancho_px, area_alto_px):
    """
    Convierte coordenadas en píxeles a milímetros basándose en las dimensiones reales del área.
    """
    relacion_x = AREA_ANCHO_MM / area_ancho_px
    relacion_y = AREA_ALTO_MM / area_alto_px
    x_mm = x_px * relacion_x
    y_mm = y_px * relacion_y
    return x_mm, y_mm

def medir_distancia_mm(p1_px, p2_px, area_ancho_px, area_alto_px):
    """
    Calcula la distancia entre dos puntos en milímetros.
    """
    x1_mm, y1_mm = convertir_px_a_mm(p1_px[0], p1_px[1], area_ancho_px, area_alto_px)
    x2_mm, y2_mm = convertir_px_a_mm(p2_px[0], p2_px[1], area_ancho_px, area_alto_px)
    distancia = math.sqrt((x2_mm - x1_mm)**2 + (y2_mm - y1_mm)**2)
    return distancia

def main():
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        quit()

    # Leer el primer cuadro para seleccionar el área de trabajo
    ret, frame = cap.read()
    if not ret:
        print("No se pudo capturar el primer cuadro.")
        cap.release()
        return

    # Seleccionar el área de trabajo manualmente
    x, y, w, h = seleccionar_area_de_trabajo(frame)
    print(f"Área seleccionada: x={x}, y={y}, w={w}, h={h}")

    puntos = []  # Lista para almacenar puntos seleccionados

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Recortar el área de trabajo seleccionada
        area_trabajo = frame[int(y):int(y+h), int(x):int(x+w)]

        # Dibujar puntos seleccionados
        for punto in puntos:
            cv2.circle(area_trabajo, punto, 5, (0, 0, 255), -1)

        # Mostrar la región recortada
        cv2.imshow("Área de Trabajo", area_trabajo)

        # Detectar clics del mouse para seleccionar puntos
        def seleccionar_punto(event, x_p, y_p, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                puntos.append((x_p, y_p))
                if len(puntos) == 2:
                    # Medir la distancia entre los dos puntos seleccionados
                    distancia_mm = medir_distancia_mm(puntos[0], puntos[1], w, h)
                    print(f"Distancia entre puntos: {distancia_mm:.2f} mm")
                    puntos.clear()

        cv2.setMouseCallback("Área de Trabajo", seleccionar_punto)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
