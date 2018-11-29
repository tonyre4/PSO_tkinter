import random
import math
try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *

color = 'gray'

class  Particle:
    def __init__(self, x, index, goal):
        self.x = x  # Particle position

        self.v = [random.randint(-1, 1), random.randint(-1, 1)]  # velocity vector (first time is calculated randomly)
        self.index = index
        self.arrP = self.calcArrowPoint()
        self.goal = goal  # this store goal position for multiple calculations
        self.active = True  # for active movement

        # For PSO calculations
        self.BestPos = self.x[:]  # best position at begining is the x init position
        self.minZ = self.calcGoalModule()  # minimum module is from current pos to goal

        self.drawParticle()


    #####################
    # calculations methods
    def calcGoalModule(self):  # Calculates module from current x to goal
        x = self.x
        g = self.goal
        z = math.sqrt((g[0] - x[0]) ** 2 + (g[1] - x[0]) ** 2)
        return z


    def calcArrowPoint(self):  # Calcultes arrow point to draw
        x = self.x
        v = self.v
        arr = []
        arr.append(x[0] + v[0])
        arr.append(x[1] + v[1])
        return arr[:]


    def calcBx(self):  # Calculates x*
        mz = self.minZ
        cGM = self.calcGoalModule()
        if cGM < mz:
            self.minZ = cGM
            self.BestPos = self.x[:]


    ########################
    # All get and set methods
    def getBX(self):  # to get best positon of the particle that it has touched
        return self.BestPos[:]


    def getX(self):  # To get position vector
        return self.x[:]


    def getV(self):  # To get Velocity vector
        return self.v[:]


    def setX(self, x):  # To set position
        self.x = x[:]


    def setV(self, v):  # To set Velocity
        self.v = v[:]

    def setArr(self, a):
        self.arrP = a[:]

    def getIndex(self):
        return self.index

    def isActivated(self):
        return self.active


    #################
    # Graphics methods
    def move_active(self):  # Movement
        if self.active:  # if the particle is active
            self.drawParticle()  # The particle will be drawn


    def deactivateParticle(self):
        canvas.delete(self.arr)  # Delete arrow drawing
        self.active = False


    def drawParticle(self):
        #self.calcArrowPoint()
        x = self.x
        a = self.arrP
        # deleting objects from canvas
        try:
            canvas.delete(self.shape)  # Delete particle
            canvas.delete(self.arr)  # Delete vector
            canvas.delete(self.text)
        except:
            pass
        # drawing particle and arrow
        self.text = canvas.create_text(x[0], x[1] - 15, text=str(self.index))
        self.shape = canvas.create_oval(x[0] - halfparti, x[1] - halfparti, x[0] + halfparti, x[1] + halfparti,
                                fill=color)  # Circle particle drawing
        self.arr = canvas.create_line(x[0], x[1], a[0], a[1], arrow=LAST, fill="red",
                              arrowshape=(4, 5, 2))  # Arrow vector drawing
