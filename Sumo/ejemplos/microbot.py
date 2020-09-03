#RobotName: Paulina 
from RobotRL import RobotRL

ro=RobotRL()

def recto():
    ro.setVel(100,100)

def buscar():
    di=ro.getDI()
    dd=ro.getDD()
    
    if(di<100 and dd<100):
        recto()
        return
    if(di==100 and dd<100):
        irDerecha()
        return
    if(di<100 and dd==100):
        irIzquierda()
        return

def irDerecha():
    ro.setVel(-40, 40)

def irIzquierda():
    ro.setVel(40, -40)

def girar():
    ro.setVel(60, -60)

def retroceder():
    ro.setVel(-100, -100)

def parar():
    ro.setVel(0,0)

def noCaer():
    if ro.getColorPiso()>90:
        retroceder()
        ro.esperar(2)
        girar()
        ro.esperar(1)

while ro.step():
    ro.setVel(-20, 20)
    noCaer()
    buscar()
