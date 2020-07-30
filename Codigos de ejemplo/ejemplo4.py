from controller import Robot
import math
import struct

trap_colour = b'\n\n\n\xff'
swamp_colour = b'\x12\x1b \xff'
exit_colour = b'\x10\xb8\x10\xff'

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

def sendMessage(robot_type, v1, v2, carac):
    message = struct.pack('i i i c', robot_type, v1, v2, carac)
    emitter.send(message)

def sendVictimMessage():
    #deberiamos pasar como parametro que victima es y quien soy yo
    global messageSent
    position = gps.getValues()

    if not messageSent:
        sendMessage(0, int(position[0] * 100), int(position[2] * 100), b'H')
        messageSent = True

def getObjectDistance(position):
    #Viejo y querido Pitagoras
    return math.sqrt((position[0] ** 2) + (position[2] ** 2))

def nearObject(position):
    return getObjectDistance(position)  < 0.10

def getVisibleVictims():
    #get all objects the camera can see
    objects = camera.getRecognitionObjects()

    victims = []
    #para poder alinear no guardo solo la posicion de la victima, sino mi alenacion con la imagen
    for item in objects:
        if item.get_colors() == [1,1,1]:
            print("Encontre alguna victima blanca")
            #distancia con respecto a la camara
            victim_pos = item.get_position()
            #donde quedo la victima en la imagen (la tengo torcida, derecha?)
            victim_image_pos = item.get_position_on_image()

            victims.append([victim_pos,victim_image_pos])

    return victims

def stopAtHeatedVictim():
    global messageSent
    
    if left_heat_sensor.getValue() > 32 or right_heat_sensor.getValue() > 32:
        print("Encontre una victima con temperatura")
        stop()
        sendVictimMessage()
    else:
        messageSent = False

def turnToVictim(victim):
    # [x,y]
    print("Trato de quedar de frente a la victima")
    position_on_image = victim[1]

    width = camera.getWidth()
    center = width / 2

    victim_x_position = position_on_image[0]
    dx = center - victim_x_position

    if dx < 0:
        turn_right_to_victim()
    else:
        turn_left_to_victim()


def getClosestVictim(victims):
    shortestDistance = 999
    closestVictim = []

    #recorro las victimas para elegir la mas cercana
    for victim in victims:
        dist = getObjectDistance(victim[0])
        if dist < shortestDistance:
            shortestDistance = dist
            closestVictim = victim

    return closestVictim

def stopAtVictim():
    global messageSent
    victims = getVisibleVictims()

    foundVictim = False

    #si tengo alguna victima apunto a la mas cercana
    if len(victims) != 0:
        closest_victim = getClosestVictim(victims)
        turnToVictim(closest_victim)

    for victim in victims:
        if nearObject(victim[0]):
            print("Encontre una victima y estoy cerca")
            stop()
            sendVictimMessage()
            foundVictim = True

    if not foundVictim:
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
            if leftSensors[i].getValue() > 80:
                turn_right()
            elif rightSensors[i].getValue() > 80:
                turn_left()
        
        if frontSensors[0].getValue() > 80 and frontSensors[1].getValue() > 80:
            spin()

        stopAtVictim()
        #Analiza si tengo victimas por temperatura
        stopAtHeatedVictim()

        avoidTiles()

        #Si paso un rato y llegue a verde entonces aviso que sali. Puedo salir en cualquier momento, mmmm
        if (robot.getTime() - program_start) > 20:
            if colour_camera.getImage() == exit_colour:
                sendMessage(0,0,0,b'E')

    
