"""Roboliga Supervisor Controller v1
   Written by Ricardo Moran and Gonzalo Zabala (CAETI - UAI) based on the work of Robbie Goldman and Alfred Roberts
"""

from controller import Supervisor
import os
import random
import struct
import math
import datetime

# Settings
timeElapsed = 0
lastTime = -1
numReloc=0
timeReloc=15
timeOut=20
lossDistance=0.76

# Create the instance of the supervisor class
supervisor = Supervisor()

# Get this supervisor node - so that it can be rest when game restarts
mainSupervisor = supervisor.getFromDef("MAINSUPERVISOR")

# Maximum time for a match
maxTime = 2.5 * 60

DEFAULT_MAX_VELOCITY = 30


class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, data):
        return self.queue.append(data)

    def dequeue(self):
        return self.queue.pop(0)

    def peek(self):
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0


class RobotHistory(Queue):
    def __init__(self):
        super().__init__()

    def enqueue(self, data):
        if len(self.queue) > 8:
            self.dequeue()
        return self.queue.append(data)


class Robot:
    '''Robot object to hold values whether its in a base or holding a human'''

    def __init__(self, node):


        self.wb_node = node

        self.wb_translationField = self.wb_node.getField('translation')
        self.wb_rotationField = self.wb_node.getField('rotation')

        self.history = RobotHistory()

        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None

        self.message = []

        self.inSimulation = True

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
        posy=self.position[1]
        return(vel[1]>0.8 or posy>0.12)

def getPath(number: int) -> str:
    '''Get the path to the correct controller'''
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


def resetControllerFile(number: int) -> None:
    '''Open the controller at the file location and blanks it'''
    filePath = getPath(number)

    if filePath != None:
        controllerFile = open(filePath, "w")
        controllerFile.close()


def createController(number: int, fileData: list) -> list:
    '''Opens the controller at the file location and writes the data to it'''
    try:
        filePath = getPath(number)

        if filePath == None:
            return None, None

        controllerFile = open(filePath, "w")
        controllerFile.write(fileData)
        controllerFile.close()

        # If there is a name in the file
        if "RobotName:" in fileData:
            # Find the name
            name = fileData[fileData.index("RobotName:") + 10:]
            name = name.split("\n")[0]
            # Return data with a name
            return name, number

        supervisor.wwiSendText("alert,ERROR: El robot no tiene nombre")
        # Return data without a name
        return None, None
    except Exception as ex:
        supervisor.wwiSendText("alert,ERROR: El archivo no es un controlador válido")
        return None, None


def assignController(num: int, name: str) -> None:
    '''Send message to robot window to say that controller has loaded and with what name'''

    if name == None:
        name = "None"

    name = name.strip()

    if num == 0:
        supervisor.wwiSendText("loaded0," + name)

    if num == 1:
        supervisor.wwiSendText("loaded1," + name)


def resetController(num: int) -> None:
    '''Send message to robot window to say that controller has been unloaded'''
    if num == 0:
        resetControllerFile(0)
        supervisor.wwiSendText("unloaded0")
    if num == 1:
        resetControllerFile(1)
        supervisor.wwiSendText("unloaded1")


def updateHistory():
    supervisor.wwiSendText(
        "historyUpdate" + "," + ",".join(robot0Obj.history.queue))



def relocate(num):
    #num indica el nro de vez que lo relocaliza
    robot0Obj.position = randomizePosition([-0.2, 0.0217, 0])
    robot1Obj.position = randomizePosition([0.2, 0.0217, 0])

    if int(num) == 0: #Mira uno para cada lado, hacia afuera
        robot0Obj.rotation = randomizeRotation([0,1,0,1.57])
        robot1Obj.rotation = randomizeRotation([0,1,0,4.71])
    elif int(num) == 1: #Como en el arranque pero al revés
        robot0Obj.rotation = randomizeRotation([0,1,0,3.15])
        robot1Obj.rotation = randomizeRotation([0,1,0,0])
    elif int(num) == 2: #enfrentados
        robot0Obj.rotation = randomizeRotation([0,1,0,4.71])
        robot1Obj.rotation = randomizeRotation([0,1,0,1.57])
    else: #Con la misma rotación con la que venían (pero parados!)
        robot0Obj.rotation = randomizeRotation([0,1,0,robot0Obj.rotation[3]])
        robot1Obj.rotation = randomizeRotation([0,1,0,robot1Obj.rotation[3]])

    robot0Obj.history.enqueue("Relocalizacion nro: "+str(num))
    updateHistory()

def distancia(pos):
    return(math.sqrt(pos[0]*pos[0]+pos[2]*pos[2]))


def write_log(r0, r1, winner, reason, time):
    '''Write log file'''
    # Get log text
    log_str = str(r0).rstrip("\r\n")+","+str(r1).rstrip("\r\n")+","+str(winner).rstrip("\r\n")+","+reason+","+time+"\n"
    # Get relative path to logs dir
    filePath = os.path.dirname(os.path.abspath(__file__))
    filePath = filePath.replace('\\', '/')
    filePath = filePath + "/../../logs/"

    # Create file name using date and time
    file_date = datetime.datetime.now()
    logFileName = file_date.strftime("log %m-%d-%y %H,%M,%S")

    filePath += logFileName + ".txt"

    try:
        # Write file
        logsFile = open(filePath, "w")
        logsFile.write(log_str)
        logsFile.close()
    except:
        # If write file fails, most likely due to missing logs dir
        print("Couldn't write log file, no log directory ./game/logs")

def randomize(value, max):
    return value + (random.random() * 2 - 1) * max

def randomizeRotation(vector):
    return [vector[0], vector[1], vector[2], randomize(vector[3], 0.1)]

def randomizePosition(vector):
    max_pos = 0.015
    return [randomize(vector[0], max_pos),
            vector[1],
            randomize(vector[2], max_pos)]

# Not currently running the match
currentlyRunning = False
previousRunState = False

# The game has not yet started
gameStarted = False

# Get the robot nodes by their DEF names
robot0 = supervisor.getFromDef("Rojo")
robot1 = supervisor.getFromDef("Verde")

if robot0 == None:
    filePath = os.path.dirname(os.path.abspath(__file__))
    filePath = filePath.replace('\\', '/')

    root = supervisor.getRoot()
    root_children_field = root.getField('children')
    root_children_field.importMFNode(12,filePath + '/../../nodes/robot0.wbo')
    robot0 = supervisor.getFromDef("Rojo")

if robot1 == None:
    filePath = os.path.dirname(os.path.abspath(__file__))
    filePath = filePath.replace('\\', '/')

    root = supervisor.getRoot()
    root_children_field = root.getField('children')
    root_children_field.importMFNode(13,filePath + '/../../nodes/robot1.wbo')
    robot1 = supervisor.getFromDef("Verde")


# Init both robots as objects to hold their info
robot0Obj = Robot(robot0)
robot1Obj = Robot(robot1)

# Both robots start in bases
# robot0InCheckpoint = True
# robot1InCheckpoint = True

# The simulation is running
simulationRunning = True
finished = False

# Reset the controllers
resetControllerFile(0)
resetControllerFile(1)

# Starting scores
# score0 = 0
# score1 = 0


# Send message to robot window to perform setup
supervisor.wwiSendText("startup")

# For checking the first update with the game running
first = True

robot0Obj.position = randomizePosition([-0.2, 0.0217, 0])
robot0Obj.rotation = randomizeRotation([0, 1, 0, 0])
robot1Obj.position = randomizePosition([0.2, 0.0217, 0])
robot1Obj.rotation = randomizeRotation([0, 1, 0, 0])


# Until the match ends (also while paused)
while simulationRunning:
    r0ts=robot0Obj.timeStopped()
    r1ts=robot1Obj.timeStopped()
    # The first frame of the game running only
    if first and currentlyRunning:
        # Restart both controllers
        robot0.restartController()
        robot1.restartController()
        first = False

    if robot0Obj.inSimulation:

        if(robot0Obj.outOfDohyo() and robot1Obj.outOfDohyo()):
            finished=True
            robot0Obj.inSimulation=False
            robot1Obj.inSimulation=False
            write_log(robot0Obj._name,robot1Obj._name, "Empate", "Salida dohyo ambos", str(timeElapsed) )
            supervisor.wwiSendText("draw")

        if(robot0Obj.outOfDohyo()):
            finished=True
            robot0Obj.inSimulation=False
            robot1Obj.inSimulation=False
            write_log(robot0Obj._name,robot1Obj._name, robot1Obj._name, "Salida dohyo", str(timeElapsed))
            supervisor.wwiSendText("lostJ1")

    if robot1Obj.inSimulation:
        if(robot1Obj.outOfDohyo()):
            finished=True
            robot0Obj.inSimulation=False
            robot1Obj.inSimulation=False
            write_log(robot0Obj._name,robot1Obj._name, robot0Obj._name, "Salida dohyo", str(timeElapsed))
            supervisor.wwiSendText("lostJ2")


    if robot0Obj.inSimulation and robot1Obj.inSimulation:
        #Si tienen una diferencia de 3 o menos y uno de los dos superó los 15, mandamos los dos a reloquearse
        #sino
        #si uno supero los 20, perdió

        if max(r0ts, r1ts)>timeReloc and abs(r0ts-r1ts)<=3:
            relocate(numReloc)
            numReloc+=1
            robot0Obj._timeStopped = 0
            robot0Obj._stopped = False
            robot0Obj._stoppedTime = None
            robot1Obj._timeStopped = 0
            robot1Obj._stopped = False
            robot1Obj._stoppedTime = None

        elif r0ts>timeOut:
            finished=True
            robot0Obj.inSimulation=False
            robot1Obj.inSimulation=False
            write_log(robot0Obj._name,robot1Obj._name, robot1Obj._name, "Timeout", str(timeElapsed))
            supervisor.wwiSendText("lostJ1")
        elif r1ts>timeOut:
            finished=True
            robot0Obj.inSimulation=False
            robot1Obj.inSimulation=False
            write_log(robot0Obj._name,robot1Obj._name, robot0Obj._name, "Timeout", str(timeElapsed))
            supervisor.wwiSendText("lostJ2")


    # If the running state changes
    if previousRunState != currentlyRunning:
        # Update the value and #print
        previousRunState = currentlyRunning
        #print("Run State:", currentlyRunning)


    # Get the message in from the robot window(if there is one)
    message = supervisor.wwiReceiveText()
    # If there is a message
    if message != "":
        # split into parts
        parts = message.split(",")
        # If there are parts
        if len(parts) > 0:
            if parts[0] == "run":
                # Start running the match
                currentlyRunning = True
                lastTime = supervisor.getTime()
                gameStarted = True
            if parts[0] == "pause":
                # Pause the match
                currentlyRunning = False
            if parts[0] == "reset":
                #print("Reset message Received")
                # Reset both controller files
                resetControllerFile(0)
                resetControllerFile(1)

                # Reset the simulation
                supervisor.simulationReset()
                simulationRunning = False
                # Restart this supervisor
                mainSupervisor.restartController()

            if parts[0] == "robot0File":

                # Load the robot 0 controller
                if not gameStarted:
                    data = message.split(",", 1)
                    if len(data) > 1:
                        name, id = createController(0, data[1])
                        if name is not None:
                            robot0Obj._name=name
                            assignController(id, name)
                else:
                    print("Please choose controllers before simulation starts.")
            if parts[0] == "robot1File":
                # Load the robot 1 controller
                if not gameStarted:
                    data = message.split(",", 1)
                    if len(data) > 1:
                        name, id = createController(1, data[1])
                        if name is not None:
                            robot1Obj._name=name
                            assignController(id, name)
                else:
                    print("Please choose controllers before simulation starts.")
            if parts[0] == "robot0Unload":
                # Unload the robot 0 controller
                if not gameStarted:
                    resetController(0)
            if parts[0] == "robot1Unload":
                # Unload the robot 1 controller
                if not gameStarted:
                    resetController(1)
            if parts[0] == 'relocate':
                data = message.split(",", 1)
                if len(data) > 1:
                    relocate(data[1])
                pass

    # Send the update information to the robot window
    supervisor.wwiSendText(
        "update," + str(timeElapsed)+","+str(r0ts)+","+str(r1ts))

    # If the time is up
    if timeElapsed >= maxTime:
        finished = True
        write_log(robot0Obj._name,robot1Obj._name, "Empate", "Fin tiempo", str(timeElapsed))
        supervisor.wwiSendText("draw")

    if(robot0Obj.crashed() or robot1Obj.crashed()):
        finished = True
        write_log(robot0Obj._name,robot1Obj._name, "Cancelado", "Crash", str(timeElapsed))
        supervisor.wwiSendText("crash")

    # If the match is running
    if currentlyRunning and not finished:
        # Get the time since the last frame
        frameTime = supervisor.getTime() - lastTime
        # Add to the elapsed time
        timeElapsed = timeElapsed + frameTime
        # Get the current time
        lastTime = supervisor.getTime()
        # Step the simulation on
        step = supervisor.step(32)
        # If the simulation is terminated or the time is up
        if step == -1:
            # Stop simulating
            simulationRunning = False
