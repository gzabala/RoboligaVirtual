from controller import Robot
import time

timeStep = 32
max_velocity = 6.28

robot = Robot()

wheel_left = robot.getMotor("left wheel motor")
wheel_right = robot.getMotor("right wheel motor")

wheel_left.setPosition(float("inf"))
wheel_right.setPosition(float("inf"))

while robot.step(timeStep) != -1:
    wheel_left.setVelocity(1.28)
    wheel_right.setVelocity(6.28)