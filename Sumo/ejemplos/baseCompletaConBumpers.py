#RobotName: Quisquilloso
from RobotRL import RobotRL

robot = RobotRL()

def recto():
    robot.setVI(100)
    robot.setVD(100)

def retroceder():
    robot.setVI(-100)
    robot.setVD(-100)

def irIzquierda():
    robot.setVI(-40)
    robot.setVD(40)

def irDerecha():
    robot.setVI(40)
    robot.setVD(-40)

def parar():
    robot.setVI(0)
    robot.setVD(0)

def buscar():
    # Guardo los valores de los sensores de distancia
    di = robot.getDI()
    dd = robot.getDD()
    #Si veo algo en los dos voy para adelante
    if ((di < 100) and (dd < 100)):
        recto()
    #si veo solo en el derecho
    elif ((di == 100) and (dd < 100)):
        irDerecha()
    #si veo solo en el izquierdo
    elif ((di < 100) and (dd == 100)):
        irIzquierda()

def noCaer():
    if (robot.getColorPiso() > 90):
        retroceder()
        robot.esperar(1)
        irIzquierda()
        robot.esperar(0.5)

def noMeToques():
    if(robot.getBI() and robot.getBD()): #si tengo los dos bumpers activados
        retroceder()

while robot.step():
    robot.setVel(30, -30)
    buscar()
    noMeToques()
    noCaer()
    #siempre dejar lo mas critico al final, porque ese es el estado en el que quedara si se cumple la
    #condicion de esa llamada
