#RobotName: UsoDeEspera
#NO SE PUEDEN USAR TILDES EN LOS COMENTARIOS
from RobotRL import RobotRL

robot = RobotRL()

while robot.step():
    robot.setVel(20, -20)
    robot.esperar(1) # El robot estara 1 segundo en el estado en el que se encuentra. En este caso, girando.
    robot.setVel(-20, 20)
    robot.esperar(1)
    # el codigo que se encuentra dentro del while se repetira una y otra vez hasta que se detenga el simulador.
    print("Comienzo otro ciclo") # Los prints aparecen en la consola de la parte inferior del Webots
    
