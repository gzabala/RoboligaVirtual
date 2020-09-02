#RobotName: Paulina 
from RobotRL import RobotRL

ro=RobotRL("Paulina")

def recto():
    ro.setVel(1,1)

def buscar():
    di=ro.getDI()
    dd=ro.getDD()
    print("DI: "+str(di)+" DD: "+str(dd))
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
    ro.setVel(-0.4, 0.4)

def irIzquierda():
    ro.setVel(0.4, -0.4)

def girar():
    ro.setVel(0.6, -0.6)

def retroceder():
    ro.setVel(-1, -1)

def parar():
    ro.setVel(0,0)

def noCaer():
    if ro.getColorPiso()>90:
        retroceder()
        ro.esperar(2)
        girar()
        ro.esperar(1)

while ro.step():
    ro.setVel(-0.2, 0.2)
    noCaer()
    buscar()
