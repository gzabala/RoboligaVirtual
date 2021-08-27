"""Roboliga Supervisor Controller v1
   Written by Ricardo Moran and Gonzalo Zabala (CAETI - UAI) based on the work of Robbie Goldman and Alfred Roberts
"""

from controller import Supervisor
import os
import random
import struct
import math
import datetime

from utils import TIME_RELOC, TIME_OUT
from Robot import Robot

timeElapsed = 0
lastTime = -1
numReloc=0

# Create the instance of the supervisor class
supervisor = Supervisor()

# Get this supervisor node - so that it can be rest when game restarts
mainSupervisor = supervisor.getFromDef("MAINSUPERVISOR")

# Maximum time for a match
maxTime = 2.5 * 60

DEFAULT_MAX_VELOCITY = 30

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
        "historyUpdate" + "," + ",".join(robots[0].history.queue))



def relocate(num):
    #num indica el nro de vez que lo relocaliza
    robots[0].position = randomizePosition([-0.2, 0.0217, 0])
    robots[1].position = randomizePosition([0.2, 0.0217, 0])

    if int(num) == 0: #Mira uno para cada lado, hacia afuera
        robots[0].rotation = randomizeRotation([0,1,0,1.57])
        robots[1].rotation = randomizeRotation([0,1,0,4.71])
    elif int(num) == 1: #Como en el arranque pero al revés
        robots[0].rotation = randomizeRotation([0,1,0,3.15])
        robots[1].rotation = randomizeRotation([0,1,0,0])
    elif int(num) == 2: #enfrentados
        robots[0].rotation = randomizeRotation([0,1,0,4.71])
        robots[1].rotation = randomizeRotation([0,1,0,1.57])

    robots[0].history.enqueue("Relocalizacion nro: "+str(num))
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
robots = [None, None]
robots[0] = Robot(0, supervisor, "Rojo")
robots[1] = Robot(0, supervisor, "Verde")


# The simulation is running
simulationRunning = True
finished = False

# Reset the controllers
resetControllerFile(0)
resetControllerFile(1)


# Send message to robot window to perform setup
supervisor.wwiSendText("startup")

# For checking the first update with the game running
first = True

robots[0].position = randomizePosition([-0.2, 0.0217, 0])
robots[0].rotation = randomizeRotation([0, 1, 0, 0])
robots[1].position = randomizePosition([0.2, 0.0217, 0])
robots[1].rotation = randomizeRotation([0, 1, 0, 0])


# Until the match ends (also while paused)
while simulationRunning:
    r0ts=robots[0].timeStopped()
    r1ts=robots[1].timeStopped()
    # The first frame of the game running only
    if first and currentlyRunning:
        # Restart both controllers
        robots[0].restartController()
        robots[1].restartController()
        first = False

    if robots[0].inSimulation:

        if(robots[0].outOfDohyo() and robots[1].outOfDohyo()):
            finished=True
            robots[0].inSimulation=False
            robots[1].inSimulation=False
            write_log(robots[0]._name,robots[1]._name, "Empate", "Salida dohyo ambos", str(timeElapsed) )
            supervisor.wwiSendText("draw")

        if(robots[0].outOfDohyo()):
            finished=True
            robots[0].inSimulation=False
            robots[1].inSimulation=False
            write_log(robots[0]._name,robots[1]._name, robots[1]._name, "Salida dohyo", str(timeElapsed))
            supervisor.wwiSendText("lostJ1")

    if robots[1].inSimulation:
        if(robots[1].outOfDohyo()):
            finished=True
            robots[0].inSimulation=False
            robots[1].inSimulation=False
            write_log(robots[0]._name,robots[1]._name, robots[0]._name, "Salida dohyo", str(timeElapsed))
            supervisor.wwiSendText("lostJ2")


    if robots[0].inSimulation and robots[1].inSimulation:
        #Si tienen una diferencia de 3 o menos y uno de los dos superó los 15, mandamos los dos a reloquearse
        #sino
        #si uno supero los 20, perdió

        if max(r0ts, r1ts)>TIME_RELOC and abs(r0ts-r1ts)<=3:
            relocate(numReloc)
            numReloc+=1
            robots[0]._timeStopped = 0
            robots[0]._stopped = False
            robots[0]._stoppedTime = None
            robots[1]._timeStopped = 0
            robots[1]._stopped = False
            robots[1]._stoppedTime = None

        elif r0ts>TIME_OUT:
            finished=True
            robots[0].inSimulation=False
            robots[1].inSimulation=False
            write_log(robots[0]._name,robots[1]._name, robots[1]._name, "Timeout", str(timeElapsed))
            supervisor.wwiSendText("lostJ1")
        elif r1ts>TIME_OUT:
            finished=True
            robots[0].inSimulation=False
            robots[1].inSimulation=False
            write_log(robots[0]._name,robots[1]._name, robots[0]._name, "Timeout", str(timeElapsed))
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
                            robots[0]._name=name
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
                            robots[1]._name=name
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
        write_log(robots[0]._name,robots[1]._name, "Empate", "Fin tiempo", str(timeElapsed))
        supervisor.wwiSendText("draw")

    if(robots[0].crashed() or robots[1].crashed()):
        finished = True
        write_log(robots[0]._name,robots[1]._name, "Cancelado", "Crash", str(timeElapsed))
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
