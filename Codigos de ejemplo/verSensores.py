from controller import Robot
from controller import LED
from controller import Accelerometer

timeStep = 32
max_velocity = 6.28

robot = Robot()

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


while robot.step(timeStep) != -1:
    print(frontSensors[0].getValues())