import os
import dynamixel_sdk as dxl  # Importa la biblioteca DynamixelSDK

# Configuración de la comunicación
DEVICENAME = 'COM15'  # Cambia según tu sistema operativo. En Windows sería algo como COM1
BAUDRATE = 9600  # Baudrate típico para AX-12A
PROTOCOL_VERSION = 1.0  # AX-12A usa el protocolo 1.0
DXL_ID_1 = 1  # ID del primer servo
DXL_ID_2 = 2  # ID del segundo servo
DXL_ID_3 = 3  # ID del tercer servo

# Dirección de control
ADDR_MX_TORQUE_ENABLE = 24
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DXL_MOVING_STATUS_THRESHOLD = 10  # Umbral de movimiento
ADDR_MX_MOVING_SPEED = 32  # Dirección de control para la velocidad de movimiento

# Definir límites de ángulo (en grados)
MIN_ANGLE = -60
MAX_ANGLE = 60


# Ángulos deseados para cada servo
A1 = 0
A2 = -35
A3 = -35


# Inicializa el puerto
portHandler = dxl.PortHandler(DEVICENAME)

# Inicializa el paquete de datos
packetHandler = dxl.PacketHandler(PROTOCOL_VERSION)

# Abre el puerto
if portHandler.openPort():
    print("Puerto abierto exitosamente")
else:
    print("Fallo al abrir el puerto")
    quit()

# Configura el baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Baudrate configurado exitosamente")
else:
    print("Fallo al configurar el baudrate")
    quit()

# Función para habilitar el torque en un servo
def enable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != dxl.COMM_SUCCESS:
        print(f"Error de comunicación en servo {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error de paquete en servo {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Torque habilitado en servo {dxl_id}")

# Habilitar torque para los tres servos
enable_torque(DXL_ID_1)
enable_torque(DXL_ID_2)
enable_torque(DXL_ID_3)

# Función para mover el servo a una posición deseada (en términos de ángulo)
def move_servo(dxl_id, angle):
    # Limitar el ángulo entre MIN_ANGLE y MAX_ANGLE
    if angle < MIN_ANGLE:
        angle = MIN_ANGLE
    elif angle > MAX_ANGLE:
        angle = MAX_ANGLE

    # Convertir el ángulo al rango de posición (0-1023)
    # El ángulo -60 se mapea a 0, y 60 se mapea a 1023
    goal_position = int(((angle + 60) / 120.0) * 1023)

    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_GOAL_POSITION, goal_position)
    if dxl_comm_result != dxl.COMM_SUCCESS:
        print(f"Error de comunicación en servo {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error de paquete en servo {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Servo {dxl_id} movido a {angle} grados")


# Función para ajustar la velocidad de torque en un servo
def set_moving_speed(dxl_id, speed):
    dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, dxl_id, ADDR_MX_MOVING_SPEED, speed)
    if dxl_comm_result != dxl.COMM_SUCCESS:
        print(f"Error de comunicación en servo {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error de paquete en servo {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Velocidad de movimiento ajustada en servo {dxl_id} a {speed}")


set_moving_speed(DXL_ID_1, 50)
set_moving_speed(DXL_ID_2, 50)
set_moving_speed(DXL_ID_3, 50)

# Mover el primer servo 
move_servo(DXL_ID_1, A1)

# Mover el segundo servo 
move_servo(DXL_ID_2, A2)

# Mover el tercer servo 
move_servo(DXL_ID_3, A3)

# Función para deshabilitar el torque cuando termines
def disable_torque(dxl_id):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != dxl.COMM_SUCCESS:
        print(f"Error de comunicación en servo {dxl_id}: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Error de paquete en servo {dxl_id}: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Torque deshabilitado en servo {dxl_id}")

'''
disable_torque(DXL_ID_1)
disable_torque(DXL_ID_2)
disable_torque(DXL_ID_3)
'''
portHandler.closePort()
