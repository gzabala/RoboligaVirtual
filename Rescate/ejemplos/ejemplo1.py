from controller import Robot

timeStep = 32
max_velocity = 6.28

robot = Robot()

wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

leftSensors = []
rightSensors = []
frontSensors = []

frontSensors.append(robot.getDistanceSensor("ps7"))
frontSensors[0].enable(timeStep)
frontSensors.append(robot.getDistanceSensor("ps0"))
frontSensors[1].enable(timeStep)

rightSensors.append(robot.getDistanceSensor("ps1"))
rightSensors[0].enable(timeStep)
rightSensors.append(robot.getDistanceSensor("ps2"))
rightSensors[1].enable(timeStep)

leftSensors.append(robot.getDistanceSensor("ps6"))
leftSensors[0].enable(timeStep)
leftSensors.append(robot.getDistanceSensor("ps5"))
leftSensors[1].enable(timeStep)

wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

def turn_right():
    setVel(0.6, -0.2)

def turn_left():
    setVel(-0.2, 0.6)

def spin():
    setVel(0.6, -0.6)

def parar():
    setVel(0,0)

def setVel(vl, vr):
    wheel_left.setVelocity(vl*max_velocity)
    wheel_right.setVelocity(vr*max_velocity)


while robot.step(timeStep) != -1:
    setVel(1,1)
    for i in range(2): 
        #si algun sensor de la izquierda da positivo
        if leftSensors[i].getValue() > 80:
            turn_right()
        #si alguno de la derecha da positivo
        elif rightSensors[i].getValue() > 80:
            turn_left()
    
    #si los dos sensores de frente dan positivo
    if frontSensors[0].getValue() > 80 and frontSensors[1].getValue() > 80:
        spin()

    #las velocidades i y d que tenga en este punto son las que realmente se van a activar