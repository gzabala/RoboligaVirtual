#RobotName: EjemploBasico
#NO SE PUEDEN USAR TILDES EN LOS COMENTARIOS
from RobotRL import RobotRL

robot = RobotRL()

while robot.step():
    # Todo el codigo que esta por encima de esta linea es obligatorio, debe estar en todo lo que programes.

    # El robot simplemente gira sobre su propio eje
    # Si te aparece texto rojo en la consola (parte inferior del simulador) es que algo esta mal...
    robot.setVel(100, 0)
    
    
