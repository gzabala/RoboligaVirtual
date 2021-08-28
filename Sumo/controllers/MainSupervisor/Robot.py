import os
import math
import traceback

from ProtoCreator import createProto
from utils import *

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

    def __init__(self, id, supervisor, node_name):
        self.id = id
        self.supervisor = supervisor
        self.node_name = node_name
        self.wb_node = None

        self.inSimulation = False

        self.history = RobotHistory()

        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None

        self.message = []

        self._name=""

    def loadRobot(self, fileName):
        if self.inSimulation: return
        try:
            self.loadController(fileName)
            self.createProto(os.path.splitext(fileName)[0] + ".json")
            self.addRobotToSimulation()
        except:
            traceback.print_exc()

    def createProto(self, fileName):
        color = "rojo" if self.id == 0 else "verde"
        proto = None
        try:
            with open(fileName, "r") as file:
                proto = createProto(file.read(), color)
        except:
            print("Loading proto failed for robot " + self.node_name + ". Using base.proto")
            with open("../../protos/base.proto", "r") as file:
                proto = file.read().replace("MicrobotRL", color)

        with open("../../protos/" + color + ".proto", "w") as file:
            file.write(proto)

    def addRobotToSimulation(self):
        fileName = None
        if self.id == 0:
            fileName = "rojo"
        elif self.id == 1:
            fileName = "verde"

        # Get relative path
        filePath = os.path.dirname(os.path.abspath(__file__))

        # Get webots root
        root = self.supervisor.getRoot()
        root_children_field = root.getField('children')
        # Get .wbo file to insert into world
        if filePath[-4:] == "game":
          root_children_field.importMFNode(-2, os.path.join(filePath,'nodes/' + fileName + '.wbo'))
        else:
          root_children_field.importMFNode(-2, os.path.join(filePath, '../../nodes/' + fileName + '.wbo'))

        self.inSimulation = True

        self.wb_node = self.supervisor.getFromDef(self.node_name)
        self.wb_translationField = self.wb_node.getField('translation')
        self.wb_rotationField = self.wb_node.getField('rotation')

        if self.node_name == "Rojo":
            self.position = randomizePosition([-0.2, 0.0217, 0])
        else:
            self.position = randomizePosition([0.2, 0.0217, 0])
        self.rotation = randomizeRotation([0, 1, 0, 0])

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
        if self.wb_node is None:
            return True
        vel = self.wb_node.getVelocity()
        robotStopped = abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01 and abs(vel[2]) < 0.01
        return robotStopped

    def timeStopped(self) -> float:
        self._stopped = self._isStopped()

        # if it isn't stopped yet
        if self._stoppedTime == None:
            if self._stopped:
                # get time the robot stopped
                self._stoppedTime = self.supervisor.getTime()
        else:
            # if its stopped
            if self._stopped:
                # get current time
                currentTime = self.supervisor.getTime()
                # calculate the time the robot stopped
                self._timeStopped = currentTime - self._stoppedTime
            else:
                # if it's no longer stopped, reset variables
                self._stoppedTime = None
                self._timeStopped = 0

        return self._timeStopped

    def outOfDohyo(self) ->bool:
        return(math.sqrt(self.position[0]*self.position[0]+self.position[2]*self.position[2])>LOSS_DIST)

    def crashed(self):
        if self.wb_node is None:
            return False
        vel = self.wb_node.getVelocity()
        posy=self.position[1]
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

    def loadController(self, fileName):
        with open(fileName) as file:
            code = file.read()
            name = self.createController(code)
            if name is not None:
                self._name=name
                self.assignController(name)

    def createController(self, fileData):
        '''Opens the controller at the file location and writes the data to it'''
        try:
            filePath = self.getControllerPath()

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
                return name

            supervisor.wwiSendText("alert,ERROR: El robot no tiene nombre")
            # Return data without a name
            return None
        except Exception as ex:
            supervisor.wwiSendText("alert,ERROR: El archivo no es un controlador válido")
            return None

    def assignController(self, name) -> None:
        '''Send message to robot window to say that controller has loaded and with what name'''
        if name == None: name = "None"
        name = name.strip()
        self.supervisor.wwiSendText("loaded" + str(self.id) +"," + name)

    def resetController(self) -> None:
        '''Send message to robot window to say that controller has been unloaded'''
        self.clearController()
        self.supervisor.wwiSendText("unloaded" + str(self.id))
