from controller import Robot
from enum import Enum
import time

class Estado(Enum):
    recto= 0
    izquierda= 1
    derecha= 2
    parado=3

estActual= Estado.recto
steps=0

timeStep = 32
max_velocity = 6.28

robot = Robot()

wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

def turn_right():
    setVel(0.6, -0.2)

def turn_left():
    setVel(-0.2, 0.6)

def spin():
    setVel(0.6, -0.6)

def parar():
    setVel(0,0)

# no poner acentos en los comentarios porque le hace mal... :)
# Inicial: Hacer una funcion para que ande derecho con un unico parametro
# Avanzado: Hacer una funcion para que doble 90 grados

def setVel(vl, vr):
    wheel_left.setVelocity(vl*max_velocity)
    wheel_right.setVelocity(vr*max_velocity)

while robot.step(timeStep) != -1:
    
    setVel(1,1)
    #turn_right()
    #turn_left()
    #spin()
