
from controller import Robot
import math
import struct

trap_colour = b'\n\n\n\xff'
swamp_colour = b'\x12\x1b \xff'

timeStep = 32
max_velocity = 6.28

messageSent = False

startTime = 0
duration = 0

robot = Robot()

wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

camera = robot.getCamera("camera")
camera.enable(timeStep)
camera.recognitionEnable(timeStep)

colour_camera = robot.getCamera("colour_sensor")
colour_camera.enable(timeStep)

emitter = robot.getEmitter("emitter")

gps = robot.getGPS("gps")
gps.enable(timeStep)

leftSensors = []
rightSensors = []
frontSensors = []

frontSensors.append(robot.getDistanceSensor("ps7"))
frontSensors[0].enable(timeStep)
frontSensors.append(robot.getDistanceSensor("ps0"))
frontSensors[1].enable(timeStep)

rightSensors.append(robot.getDistanceSensor("ps1"))
rightSensors[0].enable(timeStep)
rightSensors.append(robot.getDistanceSensor("ps2"))
rightSensors[1].enable(timeStep)

leftSensors.append(robot.getDistanceSensor("ps5"))
leftSensors[0].enable(timeStep)
leftSensors.append(robot.getDistanceSensor("ps6"))
leftSensors[1].enable(timeStep)

#        [left wheel speed, right wheel speed]
speeds = [max_velocity,max_velocity]

wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

def sendMessage():
    global messageSent
    position = gps.getValues()

    if not messageSent:
        #robot type, posicion en cm, posicion en cm, tipo de victima (esto hay que perfeccionarlo luego)
        #struct.pack codifica en binario un mensaje
        message = struct.pack('i i i c', 0, int(position[0] * 100), int(position[2] * 100), b'H')
        emitter.send(message)
        messageSent = True


def nearObject(position):
    return math.sqrt((position[0] ** 2) + (position[2] ** 2)) < 0.10

def getVisibleVictims():
    #captura todos los objetos que la camara puede ver
    objects = camera.getRecognitionObjects()

    victims = []

    for item in objects:
        if item.get_colors() == [1,1,1]:
            victim_pos = item.get_position() 
            victims.append(victim_pos)

    return victims

def stopAtVictim():
    global messageSent #envio de mensajes. Con global le digo que estoy usando la variable declarada afuera y no una local

    #tomo posicion de posibles victimas (porque son blancas)    
    victims = getVisibleVictims()

    foundVictim = False

    #si estamos cerca de una victima, paramos y enviamos mensaje al supervisor
    for victim in victims:
        if nearObject(victim):
            stop()
            sendMessage()
            foundVictim = True

    #si mande un mensaje, no mando de nuevo hasta que no pierda de vista esta
    if not foundVictim:
        messageSent = False

def avoidTiles():
    global duration, startTime
    colour = colour_camera.getImage()

    if colour == trap_colour or colour == swamp_colour:
        move_backwards()
        startTime = robot.getTime()
        duration = 2


def move_backwards():
    setVel(-0.5, -0.7)

def stop():
    setVel(0, 0)

def turn_right():
    setVel(0.6, -0.2)

def turn_left():
    setVel(-0.2, 0.6)

def spin():
    setVel(0.6, -0.6)

def setVel(vl, vr):
    wheel_left.setVelocity(vl*max_velocity)
    wheel_right.setVelocity(vr*max_velocity)

def enTarea():
    #truquito para quedarme en espera
    return (robot.getTime() - startTime) < duration

while robot.step(timeStep) != -1:
    if enTarea():
        pass
    else:
        startTime = 0
        duration = 0

        setVel(1,1)

        for i in range(2):
            #si algun sensor de la izquierda da positivo
            if leftSensors[i].getValue() > 80:
                turn_right()
             #si alguno de la derecha da positivo
            elif rightSensors[i].getValue() > 80:
                turn_left()
        
       #si los dos sensores de frente dan positivo
        if frontSensors[0].getValue() > 80 and frontSensors[1].getValue() > 80:
            spin()

        stopAtVictim()

        #avoidTiles()

