from controller import Robot

class RobotRL:

    #propiedades de clase
    __timeStep = 32
    __max_velocity = 30

    def __init__(self, name):
        #propiedades de objeto
        self.nombre=name
        self.__tiempoInicio = 0
        self.__duracion = 0
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
    def setVel(self, vl, vr):
        self.__vi=vl*self.__max_velocity
        self.__vd=vr*self.__max_velocity
        self.__ruedaIzquierda.setVelocity(self.__vi)
        self.__ruedaDerecha.setVelocity(self.__vd)

    def getVI(self):
        return self.__vi

    def getVD(self):
        return self.__vd

    #Espera
    def enEspera(self):
        return (self.__robot.getTime() - self.__tiempoInicio) < self.__duracion

    def esperar(self, tiempo):
        self.__tiempoInicio=self.__robot.getTime()
        self.__duracion=tiempo

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

    def funcionando(self):
        return (self.__robot.step(self.__timeStep) != -1)
        