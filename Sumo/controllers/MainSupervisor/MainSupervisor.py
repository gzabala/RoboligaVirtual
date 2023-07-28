"""Roboliga Supervisor Controller v1
   Written by Ricardo Moran and Gonzalo Zabala (CAETI - UAI) based on the work of Robbie Goldman and Alfred Roberts
"""
from controller import Supervisor
import os
import struct
import math
import datetime

from utils import *
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

def log(msg):
    with open("log.txt", "a") as file:
        file.write(str(msg) + "\n")

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

# Not currently running the match
currentlyRunning = False
previousRunState = False

# The game has not yet started
gameStarted = False

# Get the robot nodes by their DEF names
robots = [None, None]
robots[0] = Robot(0, supervisor, "Rojo")
robots[1] = Robot(1, supervisor, "Verde")

# The simulation is running
simulationRunning = True
finished = False

# Reset the controllers
robots[0].clearController()
robots[1].clearController()

# Send message to robot window to perform setup
supervisor.wwiSendText("startup")

# Until the match ends (also while paused)
while simulationRunning:
    r0ts=robots[0].timeStopped()
    r1ts=robots[1].timeStopped()

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
    if message != "" and message != None:
        # split into parts
        parts = message.split(",")
        # If there are parts
        if len(parts) > 0:
            if parts[0] == "run":
                currentlyRunning = True
                if not gameStarted:
                    # Add robots to simulation
                    robots[0].addToSimulation()
                    robots[1].addToSimulation()
                    # Start running the match
                    lastTime = supervisor.getTime()
                    gameStarted = True
            if parts[0] == "pause":
                # Pause the match
                currentlyRunning = False
            if parts[0] == "reset":
                #print("Reset message Received")
                # Reset both controller files
                robots[0].clearController()
                robots[1].clearController()

                # Reset the simulation
                supervisor.simulationReset()
                simulationRunning = False
                # Restart this supervisor
                mainSupervisor.restartController()
                supervisor.worldReload()
            if parts[0] == "loadController":
                try:
                    data = message.split(",", 3)
                    id = int(data[1])
                    fileName = data[2]
                    fileContents = data[3]
                    if not gameStarted:
                        robots[id].loadController(fileName, fileContents)
                    else:
                        print("No se puede cambiar el controlador una vez que empezó la simulación")
                except:
                    print("No se pudo cargar el controlador")
            if parts[0] == "loadRobot":
                try:
                    data = message.split(",", 3)
                    id = int(data[1])
                    fileName = data[2]
                    fileContents = data[3]
                    if not gameStarted:
                        robots[id].loadRobot(fileName, fileContents)
                    else:
                        print("No se puede cambiar el robot una vez que empezó la simulación")
                except:
                    print("No se pudo cargar el robot")

            if parts[0] == 'relocate':
                data = message.split(",", 1)
                if len(data) > 1:
                    relocate(data[1])
                pass

    # Send the update information to the robot window
    supervisor.wwiSendText("update," + str(timeElapsed)+","+str(r0ts)+","+str(r1ts))

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
    else:
        supervisor.step(0)
