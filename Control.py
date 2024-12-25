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

# Configuración de servos
Ax12.DEVICENAME = 'COM8'
Ax12.BAUDRATE = 9600
Ax12.connect()
Servo1 = Ax12(1)
Servo2 = Ax12(2)
Servo3 = Ax12(3)
Servo1.set_moving_speed(60)
Servo2.set_moving_speed(60)
Servo3.set_moving_speed(60)

# Función de cinemática inversa basada en el paper, ajustada para el sistema θ₁=60°, θ₂=240°, θ₃=150° como origen
def inverse_kinematics_3dof(x, y, z, L1, L2, L3):
    # Solución para theta1
    if x >= 0:
        theta1 = math.degrees(math.atan2(y, x))
    else:
        theta1 = 180 - math.degrees(math.atan2(y, abs(x)))

    # Calcular r1, r2 y r3
    r1 = math.sqrt(x**2 + y**2)
    r2 = z - L1
    r3 = math.sqrt(r1**2 + r2**2)

    # Solución para phi1 y phi2
    phi1 = math.degrees(math.atan2(r2, r1))
    phi2 = math.degrees(math.acos((L2**2 + r3**2 - L3**2) / (2 * L2 * r3)))

    # Solución para theta2
    theta2 = phi1 + phi2

    # Solución para theta3
    phi3 = math.degrees(math.acos((L2**2 + L3**2 - r3**2) / (2 * L2 * L3)))
    theta3 = phi3 - 180

    # Ajustar ángulos en relación con la pose inicial
    theta1_adjusted = theta1 
    theta2_adjusted = theta2 
    theta3_adjusted = theta3 

    return theta1_adjusted, theta2_adjusted, theta3_adjusted

# Función para seleccionar área de trabajo
def seleccionar_area_de_trabajo(frame):
    roi = cv2.selectROI("Seleccione el área de trabajo", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Seleccione el área de trabajo")
    return roi

# Conversión de píxeles a milímetros
def convertir_px_a_mm(x_px, y_px, area_ancho_px, area_alto_px):
    relacion_x = AREA_ANCHO_MM / area_ancho_px
    relacion_y = AREA_ALTO_MM / area_alto_px
    x_mm = (x_px - area_ancho_px / 2) * relacion_x  # Ajustar al centro como origen
    y_mm = (y_px - area_alto_px / 2) * relacion_y  # Ajustar al centro como origen
    return x_mm, y_mm

# Función para detectar el objeto
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

# Función para mover los servos dado ángulos en grados
def move_servos(theta_base, theta_shoulder, theta_elbow):
    offset_base = 60
    offset_shoulder = 150
    offset_elbow = 150

    servo_base_angle = theta_base + offset_base
    servo_shoulder_angle = theta_shoulder + offset_shoulder
    servo_elbow_angle = theta_elbow + offset_elbow

    pos1 = Ax12.deg2raw(servo_base_angle)
    pos2 = Ax12.deg2raw(servo_shoulder_angle)
    pos3 = Ax12.deg2raw(servo_elbow_angle)

    Servo1.set_goal_position(pos1)
    Servo2.set_goal_position(pos2)
    Servo3.set_goal_position(pos3)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    Ax12.disconnect()
    quit()

# Leer el primer cuadro para seleccionar el área de trabajo
ret, frame = cap.read()
if not ret:
    print("No se pudo capturar el primer cuadro.")
    cap.release()
    Ax12.disconnect()
    quit()

x, y, w, h = seleccionar_area_de_trabajo(frame)
print(f"Área seleccionada: x={x}, y={y}, w={w}, h={h}")

# Posición inicial del brazo
move_servos(0, 0, 0)
time.sleep(1)

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

            # Calcular cinemática inversa
            try:
                theta_base, theta_shoulder, theta_elbow = inverse_kinematics_3dof(-1*x_real, 1*y_real, z_real, L1, L2, L3)
                move_servos(theta_base, theta_shoulder, theta_elbow)
            except ValueError:
                print("Punto fuera del alcance, manteniendo posición actual.")

        cv2.imshow("Área de Trabajo", area_trabajo)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupción por el usuario.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    Ax12.disconnect()
    print("Sistema apagado correctamente.")
