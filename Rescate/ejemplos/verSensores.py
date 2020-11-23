from controller import Robot
from controller import LED
from controller import Accelerometer

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

camaraI=robot.getCamera("camera_left")
camaraI.enable(timeStep)

camaraC=robot.getCamera("camera_centre")
camaraC.enable(timeStep)

camaraD=robot.getCamera("camera_right")
camaraD.enable(timeStep)

colour_camera = robot.getCamera("colour_sensor")
colour_camera.enable(timeStep)

emitter = robot.getEmitter("emitter")

gps = robot.getGPS("gps")
gps.enable(timeStep)

while robot.step(timeStep) != -1:
    wheel_left.setVelocity(0)
    wheel_right.setVelocity(0)
    #print(frontSensors[0].getValue())
    elcolor=colour_camera.getImage()
    print(elcolor)
    #print(gps.getValues())
