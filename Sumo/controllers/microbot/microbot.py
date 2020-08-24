from RobotRL import RobotRL

ro=RobotRL("Paulina")
estados=[]

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

def ejecutarEstado(est):
    est[0]()
    ro.esperar(est[1])

def sinTareas():
    return (len(estados) == 0)

def agregarEstado(estado, tiempo):
    estados.append((estado, tiempo))

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
        agregarEstado(retroceder,2)
        agregarEstado(girar, 1)

def estadoDefecto():
    ro.setVel(-0.2, 0.2)
    noCaer()
    buscar()
    
while ro.funcionando():
    #print("SI:"+str(ro.getDI()) + " SD: "+str(ro.getDD()))
    if ro.enEspera():
       pass
    else:
       if(sinTareas()):
           estadoActual=(estadoDefecto,0)
       else:
           estadoActual=estados.pop(0)
       ejecutarEstado(estadoActual)