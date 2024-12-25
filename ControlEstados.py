import numpy as np
import cv2
import time
from Ax12 import Ax12
import math
import serial  # Importar para comunicación serial con Arduino

# Longitudes de los eslabones (ajusta según tu robot)
L1, L2, L3 = 95, 105, 220  # mm

# Dimensiones reales del área seleccionada (en mm)
AREA_ANCHO_MM = 247.0
AREA_ALTO_MM = 184.0

# Rango de color en HSV para detectar objetos
COLOR_RANGES = {
    "rojo": (np.array([132, 45, 49]), np.array([179, 255, 255])),
    "verde": (np.array([44, 40, 149]), np.array([94, 206, 224])),
    "azul": (np.array([80, 83, 139]), np.array([111, 231, 255]))
}

# Offset entre el marco de la cámara y el robot (ajusta según tu setup)
offset_x = 0.0
offset_y = 220.0

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

# Configuración de comunicación serial con Arduino
arduino = serial.Serial(port='COM9', baudrate=9600, timeout=1)  # Cambiar 'COM9' por el puerto correcto

def send_to_arduino(command):
    arduino.write(f"{command}\n".encode())
    time.sleep(0.1)

# Definición de estados
ESTADO_INICIAL = 0
ESTADO_DETECCION = 1
ESTADO_POSICIONARSE = 2
ESTADO_MOVER = 3
ESTADO_AGARRAR = 4
ESTADO_DEJAR = 5
estado_actual = ESTADO_INICIAL

# Variables globales
x_real, y_real, z_real = 0, 0, 0
theta_base, theta_shoulder, theta_elbow = 0, 0, 0

# Función de cinemática inversa
def inverse_kinematics_3dof(x, y, z, L1, L2, L3):
    theta1 = math.degrees(math.atan2(y, x))
    r1 = math.sqrt(x**2 + y**2)
    r2 = z - L1
    r3 = math.sqrt(r1**2 + r2**2)
    phi1 = math.degrees(math.atan2(r2, r1))
    phi2 = math.degrees(math.acos((L2**2 + r3**2 - L3**2) / (2 * L2 * r3)))
    theta2 = phi1 + phi2
    phi3 = math.degrees(math.acos((L2**2 + L3**2 - r3**2) / (2 * L2 * L3)))
    theta3 = phi3 - 180
    return theta1, theta2, theta3

# Función para seleccionar área de trabajo
def seleccionar_area_de_trabajo(frame):
    roi = cv2.selectROI("Seleccione el área de trabajo", frame, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Seleccione el área de trabajo")
    return roi

# Función para detectar el objeto
def get_object_coordinates(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1.5, minDist=15, param1=100, param2=10, minRadius=12, maxRadius=22)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        largest_circle = max(circles, key=lambda c: c[2])
        x_c, y_c, r = largest_circle
        return x_c, y_c
    return None

# Función para mover los servos dado ángulos en grados
def move_servos(theta_base, theta_shoulder, theta_elbow, orden=True):
    offset_base = 60
    offset_shoulder = 150
    offset_elbow = 150

    servo_base_angle = theta_base + offset_base
    servo_shoulder_angle = theta_shoulder + offset_shoulder
    servo_elbow_angle = theta_elbow + offset_elbow

    servo_base_angle = max(0, min(300, servo_base_angle))
    servo_shoulder_angle = max(0, min(300, servo_shoulder_angle))
    servo_elbow_angle = max(0, min(300, servo_elbow_angle))

    pos1 = Ax12.deg2raw(servo_base_angle)
    pos2 = Ax12.deg2raw(servo_shoulder_angle)
    pos3 = Ax12.deg2raw(servo_elbow_angle)

    if orden == True:
        Servo1.set_goal_position(pos1)
        time.sleep(2)
        Servo3.set_goal_position(pos3)
        time.sleep(2)
        Servo2.set_goal_position(pos2)
        time.sleep(2)
    elif orden == False:
        Servo3.set_goal_position(pos3)
        time.sleep(2)
        Servo2.set_goal_position(pos2)
        time.sleep(2)
        Servo1.set_goal_position(pos1)
        time.sleep(2)





cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    Ax12.disconnect()
    arduino.close()
    quit()

# Selección del área de trabajo
ret, frame = cap.read()
if not ret:
    print("No se pudo capturar el primer cuadro.")
    cap.release()
    Ax12.disconnect()
    arduino.close()
    quit()

x, y, w, h = seleccionar_area_de_trabajo(frame)
print(f"Área seleccionada: x={x}, y={y}, w={w}, h={h}")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar la imagen.")
            break

        if estado_actual == ESTADO_INICIAL:
            print("Estado 0: Posición inicial del brazo.")
            move_servos(0, 90, 0, False)
            estado_actual = ESTADO_DETECCION

        elif estado_actual == ESTADO_DETECCION:
            # Recortar el área seleccionada
            area_trabajo = frame[int(y):int(y+h), int(x):int(x+w)]
            objetos_detectados = []

            # Detectar todos los colores presentes
            for color, (lower_color, upper_color) in COLOR_RANGES.items():
                result = get_object_coordinates(area_trabajo, lower_color, upper_color)
                if result is not None:
                    x_pixel, y_pixel = result
                    x_real = (x_pixel - w / 2) * AREA_ANCHO_MM / w + offset_x
                    y_real = (y_pixel - h / 2) * AREA_ALTO_MM / h + offset_y
                    z_real = 45
                    distancia = (x_real ** 2 + y_real ** 2) ** 0.5
                    objetos_detectados.append((color, x_real, y_real, z_real, distancia))
                    print(f"Color detectado: {color}, Coordenadas: X={x_real:.2f} mm, Y={y_real:.2f} mm, Z={z_real:.2f} mm")
            # Verificar si se detectó algún color
            if not objetos_detectados:
                print("No se detectaron colores en el área seleccionada.")
                Ax12.disconnect()
                arduino.close()
                quit()
            
            # Encontrar el objeto más cercano
            objeto_mas_cercano = min(objetos_detectados, key=lambda obj: obj[4])
            color_mas_cercano, x_cercano, y_cercano, z_cercano, distancia_cercana = objeto_mas_cercano

            print(f"El color más cercano es: {color_mas_cercano}")
            print(f"Coordenadas más cercanas: X={x_cercano:.2f} mm, Y={y_cercano:.2f} mm, Z={z_cercano:.2f} mm")

            estado_actual = ESTADO_POSICIONARSE


        elif estado_actual == ESTADO_POSICIONARSE:
            print("Estado 2: Calculando cinemática inversa.")
            try:
                theta_base, theta_shoulder, theta_elbow = inverse_kinematics_3dof(-1 * x_cercano, y_cercano, z_real, L1, L2, L3)
                print(f"Ángulos calculados: base={theta_base:.2f}, hombro={theta_shoulder:.2f}, codo={theta_elbow:.2f}")
                estado_actual = ESTADO_MOVER
            except ValueError:
                print("Punto fuera del alcance, volviendo al estado inicial.")
                estado_actual = ESTADO_INICIAL

        elif estado_actual == ESTADO_MOVER:
            print("Estado 3: Moviendo servos a la posición calculada.")
            move_servos(theta_base, theta_shoulder, theta_elbow)
            time.sleep(1)
            estado_actual = ESTADO_AGARRAR

        elif estado_actual == ESTADO_AGARRAR:
            print("Estado 4: Enviando comando de agarre al Arduino.")
            send_to_arduino("AGARRAR")
            time.sleep(1)
            estado_actual = ESTADO_DEJAR

        elif estado_actual == ESTADO_DEJAR:
            move_servos(0, 90, 0, False)
            move_servos(0, 55, -80, False)
            send_to_arduino("SOLTAR")

            estado_actual = ESTADO_INICIAL

        cv2.imshow("Detección de objeto", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupción del usuario.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    Ax12.disconnect()
    arduino.close()
    print("Sistema apagado correctamente.")
