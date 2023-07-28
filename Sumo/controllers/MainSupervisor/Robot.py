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
        self.wb_node = self.supervisor.getFromDef(self.node_name)

        self.color = "rojo" if self.id == 0 else "verde"

        self.inSimulation = False

        self.history = RobotHistory()

        self._timeStopped = 0
        self._stopped = False
        self._stoppedTime = None

        self.message = []

        self._name=""
        self._proto = None

        self.clearController()

    def addToSimulation(self):
        self.writeProto()

        # Get relative path
        filePath = os.path.dirname(os.path.abspath(__file__))

        # Get webots root
        root = self.supervisor.getRoot()
        root_children_field = root.getField('children')
        # Get .wbo file to insert into world
        aux=os.path.join(filePath,'nodes/' + self.color + '.wbo')
        if(self.color=='rojo'):
            root_children_field.importMFNodeFromString(-2, \
"""DEF Rojo rojo {
  translation -0.2 0.0217 0
  name "Rojo"
  controller "robot0Controller"
  extensionSlot [
    DEF equipo Solid {
      translation 0 0.024 0
      rotation -1 0 0 1.57
      children [
        DEF placa Shape {
          appearance PBRAppearance {
            baseColor 1 0 0
            metalness 0
          }
          geometry Cylinder {
            height 0.003
            radius 0.03
          }
          isPickable FALSE
        }
      ]
      boundingObject USE placa
      physics Physics {
      }
    }
  ]
}""")
        else:
            root_children_field.importMFNodeFromString(-2, \
"""DEF Verde verde {
  translation 0.2 0.0217 0
  name "Verde"
  controller "robot1Controller"
  extensionSlot [
    DEF equipo Solid {
      translation 0 0.024 0
      rotation -1 0 0 1.57
      children [
        DEF placa Shape {
          appearance PBRAppearance {
            baseColor 0 1 0
            metalness 0
          }
          geometry Cylinder {
            height 0.003
            radius 0.03
          }
          isPickable FALSE
        }
      ]
      boundingObject USE placa
      physics Physics {
      }
    }
  ]
}""")

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
        if not self.inSimulation: return True
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
        if not self.inSimulation: return False
        vel = self.wb_node.getVelocity()
        posy=self.position[1]
        return(vel[1]>0.8 or posy>0.12)

    def restartController(self):
        if not self.inSimulation: return
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

    def loadController(self, fileName, fileContents):
        code = fileContents
        name = self.createController(code)
        if name is not None:
            self._name = name
            self.assignController(name)

    def loadRobot(self, fileName, fileContents):
        data = fileContents
        proto = self.createProto(data)
        if proto is not None:
            self._proto = proto
            self.assignProto(fileName)

    def createProto(self, data):
        try:
            return createProto(data, self.color)
        except:
            traceback.print_exc()
            return None

    def writeProto(self):
        proto = self._proto
        if proto is None:
            with open("../../protos/base.proto", "r") as file:
                proto = file.read().replace("MicrobotRL", self.color)
                print(f"Cargando robot por defecto para {self.node_name}.")

        with open("../../protos/" + self.color + ".proto", "w") as file:
            file.write(proto)


    def createController(self, fileData):
        '''Opens the controller at the file location and writes the data to it'''
        try:
            filePath = self.getControllerPath()

            if filePath == None: return None

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

            self.supervisor.wwiSendText("alert,ERROR: El robot no tiene nombre")
            # Return data without a name
            return None
        except Exception as ex:
            self.supervisor.wwiSendText("alert,ERROR: El archivo no es un controlador válido")
            return None

    def assignController(self, name) -> None:
        '''Send message to robot window to say that controller has loaded and with what name'''
        if name == None: name = "None"
        name = name.strip()
        self.supervisor.wwiSendText("loadedController," + str(self.id) +"," + name)


    def assignProto(self, name) -> None:
        name = os.path.splitext(name.strip())[0]
        self.supervisor.wwiSendText("loadedProto," + str(self.id) +"," + name)

    def resetController(self) -> None:
        '''Send message to robot window to say that controller has been unloaded'''
        self.clearController()
        self.supervisor.wwiSendText("unloaded" + str(self.id))
