from controller import Robot
import math
import struct

trap_colour = b'oo\x8b\xff'
swamp_colour = b'\x8e\xde\xf5\xff'

timeStep = 32
max_velocity = 6.28

messageSent = False

startTime = 0
duration = 0

robot = Robot()

wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

camaraI=robot.getCamera("camera_left")
camaraI.enable(timeStep)

camaraC=robot.getCamera("camera_centre")
camaraC.enable(timeStep)

camaraD=robot.getCamera("camera_right")
camaraD.enable(timeStep)


colour_camera = robot.getCamera("colour_sensor")
colour_camera.enable(timeStep)

emitter = robot.getEmitter("emitter")

gps = robot.getGPS("gps")
gps.enable(timeStep)

#Sensores de temperatura
left_heat_sensor = robot.getLightSensor("left_heat_sensor")
right_heat_sensor = robot.getLightSensor("right_heat_sensor")

left_heat_sensor.enable(timeStep)
right_heat_sensor.enable(timeStep)

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


wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

program_start = robot.getTime()

def sendMessage(v1, v2, carac):
    message = struct.pack('i i c', v1, v2, carac)
    emitter.send(message)

def sendVictimMessage():
    #deberiamos pasar como parametro que victima es y quien soy yo
    global messageSent
    position = gps.getValues()

    if not messageSent:
        sendMessage(int(position[0] * 100), int(position[2] * 100), b'H')
        messageSent = True

def getObjectDistance(position):
    #Viejo y querido Pitagoras
    return math.sqrt((position[0] ** 2) + (position[2] ** 2))

def nearObject(position):
    return getObjectDistance(position)  < 0.10

def stopAtHeatedVictim():
    global messageSent, startTime, duration
    
    if left_heat_sensor.getValue() > 32 or right_heat_sensor.getValue() > 32:
        print('Encontre una victima con temperatura')
        stop()
        sendVictimMessage()
        startTime = robot.getTime()
        duration = 3.1        
    else:
        messageSent = False


def avoidTiles():
    global duration, startTime
    colour = colour_camera.getImage()

    if colour == trap_colour or colour == swamp_colour:
        move_backwards()
        startTime = robot.getTime()
        duration = 2

def turn_right_to_victim():
    setVel(1,0.8)

def turn_left_to_victim():
    setVel(0.8,1)

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
    return (robot.getTime() - startTime) < duration

while robot.step(timeStep) != -1:
    if enTarea():
        pass
    else:
        startTime = 0
        duration = 0

        setVel(1,1)

        for i in range(2):
            if leftSensors[i].getValue() < 0.05:
                turn_right()
            elif rightSensors[i].getValue() < 0.05:
                turn_left()
        
        if frontSensors[0].getValue() < 0.05 and frontSensors[1].getValue() < 0.05:
            spin()

        #Analiza si tengo victimas por temperatura
        stopAtHeatedVictim()

        avoidTiles()


    
