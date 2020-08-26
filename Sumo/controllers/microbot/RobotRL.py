from controller import Robot

class RobotRL:

    #propiedades de clase
    __timeStep = 32
    __max_velocity = 30

    def __init__(self, name):
        #propiedades de objeto
        self.nombre=name
        self.__robot = Robot()

        self.__ruedaIzquierda = self.__robot.getMotor("motorIzquierdo")
        self.__ruedaDerecha = self.__robot.getMotor("motorDerecho")

        self.__camaraPiso=self.__robot.getCamera("colorPiso")
        self.__camaraPiso.enable(self.__timeStep)

        self.__senDistI=self.__robot.getDistanceSensor("sensorDistanciaI")
        self.__senDistI.enable(self.__timeStep)

        self.__senDistD=self.__robot.getDistanceSensor("sensorDistanciaD")
        self.__senDistD.enable(self.__timeStep)

        self.__ruedaIzquierda.setPosition(float("inf"))
        self.__ruedaDerecha.setPosition(float("inf"))

        self.__vi=0
        self.__vd=0

    #Velocidad de las ruedas
    def setVel(self, vi, vd):
        self.setVI(vi)
        self.setVD(vd)

    def setVI(self, vi):
        self.__vi=vi*self.__max_velocity
        self.__ruedaIzquierda.setVelocity(self.__vi)

    def setVD(self, vd):
        self.__vd=vd*self.__max_velocity
        self.__ruedaDerecha.setVelocity(self.__vd)

    def getVI(self):
        return self.__vi

    def getVD(self):
        return self.__vd

    #Espera
    def esperar(self, duracion):
        inicio = self.tiempoActual()
        while (self.tiempoActual() - inicio) < duracion:
            self.step()

    def tiempoActual(self):
        return self.__robot.getTime()

    #funciones útiles
    def __mapeo(self, val, min, max):
        return int((val - min) * 100 / (max - min))

    #sensores
    def getColorPiso(self):
        return self.__mapeo(int.from_bytes(self.__camaraPiso.getImage(), "little"), 4281216556, 4292861922)

    def getDI(self):
        return self.__senDistI.getValue()

    def getDD(self):
        return self.__senDistD.getValue()

    def step(self):
        return (self.__robot.step(self.__timeStep) != -1)
