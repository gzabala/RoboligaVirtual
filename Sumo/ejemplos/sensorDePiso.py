#RobotName: SensorDePiso
#NO SE PUEDEN USAR TILDES EN LOS COMENTARIOS

from RobotRL import RobotRL

robot = RobotRL()

while robot.step():
    robot.setVel(50, 50) # Defino la velocidad para ir hacia adelante
    color=robot.getColorPiso() # robot.getColorPiso() devuelve un valor entre 0 (oscuro) y 100 (claro)
    print(color) #vemos en la consola los valores que toma la lectura del piso

    # si estoy viendo el blanco intentare huir
    if(robot.getColorPiso()>90): 
       robot.setVel(-30, -30) #Retrocedo
       robot.esperar(0.5) #durante medio segundo
       robot.setVI(30) #pongo la rueda izquierda a andar hacia adelante asi giro
       robot.esperar(0.5) #durante medio segundo tambien
    
    # si no vio el piso blanco, no entro en el if y siguio derecho
    
