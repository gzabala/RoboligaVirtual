"""Supervisor Controller Prototype v1
   Written by Robbie Goldman and Alfred Roberts
"""

from controller import Supervisor
import os
import random
import struct
import math
import datetime

# Settings
timeReloc=15
timeOut=20
lossDistance=0.76
maxTime = 2.5 * 60
DEFAULT_MAX_VELOCITY = 30

supervisor = Supervisor()
mainSupervisor = supervisor.getFromDef("MAINSUPERVISOR")

class Robot:
    '''Robot object to hold values whether its in a base or holding a human'''

    def __init__(self, id, node):
        self.id = id
        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')
        self.wb_rotationField = self.wb_node.getField('rotation')

        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None

        self._name=""

    @property
    def position(self) -> list:
        return self.wb_translationField.getSFVec3f()

    @position.setter
    def position(self, pos: list) -> None:
        self.wb_translationField.setSFVec3f(pos)

    @property
    def rotation(self) -> list:
        return self.wb_rotationField.getSFRotation()

    @rotation.setter
    def rotation(self, pos: list) -> None:
        self.wb_rotationField.setSFRotation(pos)

    def setMaxVelocity(self, vel: float) -> None:
        self.wb_node.getField('max_velocity').setSFFloat(vel)

    def _isStopped(self) -> bool:
        vel = self.wb_node.getVelocity()
        robotStopped = abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01 and abs(vel[2]) < 0.01
        return robotStopped

    def timeStopped(self) -> float:
        self._stopped = self._isStopped()

        # if it isn't stopped yet
        if self._stoppedTime == None:
            if self._stopped:
                # get time the robot stopped
                self._stoppedTime = supervisor.getTime()
        else:
            # if its stopped
            if self._stopped:
                # get current time
                currentTime = supervisor.getTime()
                # calculate the time the robot stopped
                self._timeStopped = currentTime - self._stoppedTime
            else:
                # if it's no longer stopped, reset variables
                self._stoppedTime = None
                self._timeStopped = 0

        return self._timeStopped

    def outOfDohyo(self) ->bool:
        return(math.sqrt(self.position[0]*self.position[0]+self.position[2]*self.position[2])>lossDistance)

    def crashed(self):
        vel = self.wb_node.getVelocity()
        posy = self.position[1]
        return(vel[1]>0.8 or posy>0.12)

    def restartController(self):
        self.wb_node.restartController()

    def resetPhysics(self):
        self.wb_node.resetPhysics()

    def getControllerPath(self) -> str:
        '''Get the path to the correct controller'''
        number = self.id

        # The current path to this python file
        filePath = os.path.dirname(os.path.abspath(__file__))
        filePath = filePath.replace('\\', '/')
        # Split into parts on \
        pathParts = filePath.split("/")

        filePath = ""
        # Add all parts back together
        for part in pathParts:
            # Except the last one
            if part != pathParts[-1]:
                # Concatenate with / not \ (prevents issues with escape characters)
                filePath = filePath + part + "/"

        # Controller number part added
        if number == 0:
            filePath = filePath + "robot0Controller/robot0Controller.py"
        elif number == 1:
            filePath = filePath + "robot1Controller/robot1Controller.py"
        else:
            # Returns none if id was not valid
            filePath = None

        return filePath

    def clearController(self):
        '''Open the controller at the file location and blanks it'''
        filePath = self.getControllerPath()

        if filePath != None:
            controllerFile = open(filePath, "w")
            controllerFile.close()

    def loadController(self, code):
        return self.createController(code)

    def createController(self, fileData):
        '''Opens the controller at the file location and writes the data to it'''
        try:
            filePath = self.getControllerPath()

            if filePath == None:
                return None

            controllerFile = open(filePath, "w")
            controllerFile.write(fileData)
            controllerFile.close()

            # If there is a name in the file
            if "RobotName:" in fileData:
                # Find the name
                name = fileData[fileData.index("RobotName:") + 10:]
                name = name.split("\n")[0]
                name = name.strip()
                self._name = name
                return name

            alert("ERROR: El robot no tiene nombre")
            # Return data without a name
            return None
        except Exception as ex:
            alert("ERROR: El archivo no es un controlador válido")
            return None



def send(message):
    separator = ","
    messageString = separator.join([str(each) for each in message])
    supervisor.wwiSendText(messageString)

def alert(msg):
    send(["alert", msg])

def log(msg):
    send(["log", msg])

def randomize(value, max):
    return value + (random.random() * 2 - 1) * max

def randomizeRotation(vector):
    return [vector[0], vector[1], vector[2], randomize(vector[3], 0.1)]

def randomizePosition(vector):
    max_pos = 0.015
    return [randomize(vector[0], max_pos),
            vector[1],
            randomize(vector[2], max_pos)]

def reset():
    supervisor.simulationResetPhysics()
    robot0.resetPhysics()
    robot0.position = randomizePosition([-0.2, 0.0217, 0])
    robot0.rotation = randomizeRotation([0, 1, 0, 0])
    robot0.restartController()
    robot1.resetPhysics()
    robot1.position = randomizePosition([0.2, 0.0217, 0])
    robot1.rotation = randomizeRotation([0, 1, 0, 0])
    robot1.restartController()

def checkForGameEnd():
    if(robot0.outOfDohyo() and robot1.outOfDohyo()):
        send(["gameEnd", -1])
        reset()
    if(robot0.outOfDohyo()):
        send(["gameEnd", 1])
        reset()
    if(robot1.outOfDohyo()):
        send(["gameEnd", 0])
        reset()
    if timeElapsed >= maxTime:
        send(["gameEnd", -1])
        reset()
    if(robot0.crashed() or robot1.crashed()):
        send(["crash"])
        reset()


def checkForRelocation():
    global numReloc
    #Si tienen una diferencia de 3 o menos y uno de los dos superó los 15, mandamos los dos a reloquearse
    #sino
    #si uno supero los 20, perdió
    if max(r0ts, r1ts)>timeReloc and abs(r0ts-r1ts)<=3:
        relocate(numReloc)
        numReloc += 1
        robot0._timeStopped = 0
        robot0._stopped = False
        robot0._stoppedTime = None
        robot1._timeStopped = 0
        robot1._stopped = False
        robot1._stoppedTime = None

    elif r0ts>timeOut:
        reset()
        send(["gameEnd", 1])
    elif r1ts>timeOut:
        reset()
        send(["gameEnd", 0])


def relocate(num):
    #num indica el nro de vez que lo relocaliza
    robot0.position = randomizePosition([-0.2, 0.0217, 0])
    robot1.position = randomizePosition([0.2, 0.0217, 0])

    if int(num) == 0: #Mira uno para cada lado, hacia afuera
        robot0.rotation = randomizeRotation([0,1,0,1.57])
        robot1.rotation = randomizeRotation([0,1,0,4.71])
    elif int(num) == 1: #Como en el arranque pero al revés
        robot0.rotation = randomizeRotation([0,1,0,3.15])
        robot1.rotation = randomizeRotation([0,1,0,0])
    elif int(num) == 2: #enfrentados
        robot0.rotation = randomizeRotation([0,1,0,4.71])
        robot1.rotation = randomizeRotation([0,1,0,1.57])


def checkIncomingMessages():
    global lastTime, gameStarted, simulationRunning
    # Get the message in from the robot window(if there is one)
    message = supervisor.wwiReceiveText()
    # If there is a message
    if message != "":
        # split into parts
        parts = message.split(",")
        # If there are parts
        if len(parts) > 0:
            if parts[0] == "loadController":
                data = message.split(",", 2)
                if len(data) > 2:
                    id = int(data[1])
                    code = data[2]
                    name = None
                    if id == 0:
                        name = robot0.loadController(code)
                    elif id == 1:
                        name = robot1.loadController(code)
                    send(["loadedController", id, name])
            if parts[0] == "start":
                reset()
                gameStarted = True
                lastTime = supervisor.getTime()
            if parts[0] == "next":
                reset()
                send(["gameEnd", -1])
            if parts[0] == "stop":
                robot0.clearController()
                robot1.clearController()
                robot0.restartController()
                robot1.restartController()

                supervisor.simulationReset()
                simulationRunning = False
                mainSupervisor.restartController()


r0ts = 0
r1ts = 1
timeElapsed = 0
lastTime = -1
numReloc=0

gameStarted = False
simulationRunning = True

robot0 = Robot(0, supervisor.getFromDef("Rojo"))
robot1 = Robot(1, supervisor.getFromDef("Verde"))

# Reset the controllers
robot0.clearController()
robot1.clearController()

robot0.restartController()
robot1.restartController()


while simulationRunning:
    checkIncomingMessages()

    if gameStarted:
        checkForGameEnd()
        checkForRelocation()

        r0ts = robot0.timeStopped()
        r1ts = robot1.timeStopped()
        frameTime = supervisor.getTime() - lastTime
        timeElapsed = timeElapsed + frameTime
        lastTime = supervisor.getTime()

        send(["update", timeElapsed, r0ts, r1ts])

    if supervisor.step(32) == -1:
        simulationRunning = False
