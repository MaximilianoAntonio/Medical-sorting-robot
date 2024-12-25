import cv2
import numpy as np

# Variables globales
hsv = None

# Función para actualizar la máscara basada en las barras deslizantes
def update_mask(*args):
    h_min = cv2.getTrackbarPos('H Min', 'Controles')
    h_max = cv2.getTrackbarPos('H Max', 'Controles')
    s_min = cv2.getTrackbarPos('S Min', 'Controles')
    s_max = cv2.getTrackbarPos('S Max', 'Controles')
    v_min = cv2.getTrackbarPos('V Min', 'Controles')
    v_max = cv2.getTrackbarPos('V Max', 'Controles')

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow('Mascara', mask)
    cv2.imshow('Resultado', result)

# Leer la imagen o video
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("No se pudo abrir la cámara o video.")
    exit()

# Crear ventanas
cv2.namedWindow('Controles')
cv2.namedWindow('Imagen')
cv2.namedWindow('Mascara')
cv2.namedWindow('Resultado')

# Crear barras deslizantes
cv2.createTrackbar('H Min', 'Controles', 0, 179, update_mask)
cv2.createTrackbar('H Max', 'Controles', 179, 179, update_mask)
cv2.createTrackbar('S Min', 'Controles', 0, 255, update_mask)
cv2.createTrackbar('S Max', 'Controles', 255, 255, update_mask)
cv2.createTrackbar('V Min', 'Controles', 0, 255, update_mask)
cv2.createTrackbar('V Max', 'Controles', 255, 255, update_mask)

while True:
    ret, frame = cap.read()
    if not ret:
        print("No se pudo leer el frame.")
        break

    # Convertir el frame a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Actualizar la máscara y mostrar la imagen original
    update_mask()
    cv2.imshow('Imagen', frame)

    # Presiona 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
