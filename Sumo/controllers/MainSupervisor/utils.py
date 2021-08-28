import random

import tkinter as tk
from tkinter import filedialog

# Settings
TIME_RELOC=15
TIME_OUT=20
LOSS_DIST=0.76


############################################################
# File dialogs
# NOTE(Richo): Important initialization! DO NOT DELETE!
root = tk.Tk()
root.wm_attributes('-topmost', 1) # Stay on top
root.withdraw() # Hide root window

def askdirectory():
    return filedialog.askdirectory()

def askfile():
    return filedialog.askopenfilename()

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
