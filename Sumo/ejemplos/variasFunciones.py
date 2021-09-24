#RobotName: FuncUtiles
from RobotRL import RobotRL

robot = RobotRL()

di = 0
dd = 0

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

def noCaer():
    if (robot.getColorPiso() > 90):
        retroceder()
        robot.esperar(2)
        irIzquierda()
        robot.esperar(1)

while robot.step():
    recto()
    noCaer()

