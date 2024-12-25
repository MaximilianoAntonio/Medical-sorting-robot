import numpy as np
import cv2
import time
from Ax12 import Ax12
import math

# Longitudes de los eslabones (ajusta según tu robot)
L1, L2, L3 = 95, 105, 220  # mm

# Dimensiones reales del área seleccionada (en mm)
AREA_ANCHO_MM = 247.0
AREA_ALTO_MM = 184.0

# Rango de color en HSV para detectar el objeto rojo (ajusta según tu entorno)
lower_red = np.array([160, 100, 100])
upper_red = np.array([179, 255, 255])

# Offset entre el marco de la cámara y el robot (ajusta según tu setup)
offset_x = 0.0
offset_y = 230.0

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    quit()

# Leer el primer cuadro para seleccionar el área de trabajo
ret, frame = cap.read()
if not ret:
    print("No se pudo capturar el primer cuadro.")
    cap.release()
    quit()

def seleccionar_area_de_trabajo(frame):
    roi = cv2.selectROI("Seleccione el área de trabajo", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Seleccione el área de trabajo")
    return roi

def convertir_px_a_mm(x_px, y_px, area_ancho_px, area_alto_px):
    relacion_x = AREA_ANCHO_MM / area_ancho_px
    relacion_y = AREA_ALTO_MM / area_alto_px
    x_mm = (x_px - area_ancho_px / 2) * relacion_x  # Ajustar al centro como origen
    y_mm = (y_px - area_alto_px / 2) * relacion_y  # Ajustar al centro como origen
    return x_mm, y_mm

def get_object_coordinates(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1.5, minDist=20,
                               param1=100, param2=10, minRadius=18, maxRadius=22)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        largest_circle = max(circles, key=lambda c: c[2])
        x_c, y_c, r = largest_circle
        cv2.circle(frame, (x_c, y_c), r, (0,255,0), 2)
        return x_c, y_c
    return None

x, y, w, h = seleccionar_area_de_trabajo(frame)
print(f"Área seleccionada: x={x}, y={y}, w={w}, h={h}")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar la imagen.")
            break

        # Recortar el área de trabajo seleccionada
        area_trabajo = frame[int(y):int(y+h), int(x):int(x+w)]

        # Dibujar el origen (0, 0)
        origen_x = int(w / 2)
        origen_y = int(h / 2)
        cv2.circle(area_trabajo, (origen_x, origen_y), 5, (255, 0, 0), -1)

        # Detectar objeto
        result = get_object_coordinates(area_trabajo, lower_red, upper_red)
        
        if result is not None:
            x_pixel, y_pixel = result

            # Convertir a coordenadas del mundo
            x_real, y_real = convertir_px_a_mm(x_pixel, y_pixel, w, h)
            x_real += offset_x  # Aplicar offset para ajustar al origen del robot
            y_real += offset_y  # Aplicar offset para ajustar al origen del robot
            z_real = 70  # Altura fija del objeto

            print(f"Coordenadas detectadas: X={x_real:.2f} mm, Y={y_real:.2f} mm, Z={z_real:.2f} mm")

        cv2.imshow("Área de Trabajo", area_trabajo)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupción por el usuario.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Sistema apagado correctamente.")
