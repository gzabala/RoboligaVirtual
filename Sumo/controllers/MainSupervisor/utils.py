import random

# Settings
TIME_RELOC=15
TIME_OUT=20
LOSS_DIST=0.76

############################################################
# Random

def randomize(value, max):
    return value + (random.random() * 2 - 1) * max

def randomizeRotation(vector):
    return [vector[0], vector[1], vector[2], randomize(vector[3], 0.1)]

def randomizePosition(vector):
    max_pos = 0.015
    return [randomize(vector[0], max_pos),
            vector[1],
            randomize(vector[2], max_pos)]
