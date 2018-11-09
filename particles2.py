try:
    # for Python2
    from Tkinter import *    
except ImportError:
    # for Python3
    from tkinter import *   

import sys
import random
import time
import math

global canvas

args = sys.argv

particles = 3
fps = 60
timing = 1000/fps
slowness = 10
anchotk = 500
altotk = 500
partiSize = 8 #Tiene que ser un numero par
halfparti = partiSize/2
tk = Tk()
canvas = Canvas(tk, width=anchotk, height=altotk, bg="white")
canvas.pack()
color = 'gray'

vbounds = 20

class Simulation:
    
    def __init__(self, np):
        #Class constants
        self.Goal= [300,400]
        self.sizeGoal = 40
        self.halfsizeBP = self.sizeGoal/2
	self.areaGoal = [self.Goal[0]-self.halfsizeBP, self.Goal[1]-self.halfsizeBP, self.Goal[0]+self.halfsizeBP, self.Goal[1]+self.halfsizeBP]
        self.alpha = 0.2
        self.beta = 0.2
	self.np = np #number of particles
        self.restrictedRespawnAreas = [[300,300,anchotk,altotk]] 
        self.obstacles = []
        self.obstaclesCoords = []
        self.readObstacles()
        self.printObstacles()

        #For avoiding some areas to respawn
        self.avoidRespawnAreas = False

        self.minZ = 4000.0 #For g*
        self.bestPos = [0,0] #For g*
        
        #animation vars
        self.animate = True #Enable this for animation options
	self.animating = False #this is to know when its animating or not
        self.fps = 0
        self.Vparts = []
        self.xtemp = []
        if self.animate:
	    self.Vt = []
            self.Vt1 = []
            self.Xt = []
            self.Xt1 = []
	
        #Class variables
	self.particles = []
	for i in range(0,self.np): #respawn particles
	    self.particles.append(Particle(self.generatePos(),self.Goal))
        
        self.Es = self.generateEs()
        self.bestPPos = self.calBestParticlePos()
        
        self.storeVt1Xt1() 
        
        #Print constant canvas objects
        self.printRegion()
        #Set refreshment loop
	self.updateParticles()

    def readObstacles(self):
        with open(args[1],"r") as f:
            for l in f:
                l = l.replace("\n","")
                l = l.split(",")
                obs = []
                for coord in l:
                    obs.append(int(coord))
                self.obstaclesCoords.append(obs)
        print "Obstacles Coords:\n",self.obstaclesCoords

    def printObstacles(self):
        for obs in self.obstaclesCoords:
            self.obstacles.append(canvas.create_rectangle(obs[0], obs[1], obs[2], obs[3], fill = 'orange'))

    def updateParticles(self):
        self.Es = self.generateEs()

	if self.animate:
	    #self.Vt = self.Vt1[:] #For animation, shift future register to present register	
            self.Xt = self.Xt1[:]
        
        if not self.animating:
            self.calVs()
	#   self.calXs()
            self.animation()

	    if self.animate:
	        self.storeVt1Xt1() #for animation
	
        if self.animating:
            self.animationfps()
	
        #if self.animate and not self.animation:
        #    self.resetVX() #Reset real values

        for p in self.particles: #print real movements
	   p.move_active(self.Goal)
        self.calBestParticlePos()
	
	for p in self.particles:
	    if self.pointIsInArea(p.getX(),self.areaGoal):
		p.active = False
        
	tk.after(timing*slowness, self.updateParticles) 
    

    def animation(self): #This function is not finished
        self.Vparts = []
        for v in self.Vt1:
            self.Vparts.append([float(v[0])/fps, float(v[1])/fps])
        print "Xts: ",self.Xt
        self.animating = True

    def animationfps(self):
        if self.fps == 0:
            timing = 1000/fps

        if self.fps == fps+1:
            self.fps = 0
            timing = 1
            self.animating = False
            return
        
        self.xtemp = []
        for j,x in enumerate(self.Xt): #calculate temporal Xs
            self.xtemp.append([x[0] + self.Vparts[j][0]*self.fps , x[1] + self.Vparts[j][1]*self.fps])
        print "fps: ",self.fps
        for j,x in enumerate(self.xtemp):
            print "X[",j,"]: ", x
        for p,x in zip(self.particles,self.xtemp):
            if self.pointIsInArea(x,[0,0,anchotk,altotk]): #If is inside of the frame, it will 
		p.setX(x)
        self.fps += 1
        return

    def resetVX(self):
        for p,b in zip(self.particles,zip(self.Vt1,self.Xt1)):
            p.setV(b[0])
            p.setX(b[1])

    def storeVtXt(self):
        self.Vt = []
        self.Xt = []
        for p in self.particles:
            self.Vt.append(p.getV())
            self.Xt.append(p.getX())
	
    def storeVt1Xt1(self):
        self.Vt1 = []
        self.Xt1 = []
        for p in self.particles:
            self.Vt1.append(p.getV())
            self.Xt1.append(p.getX())


    def calXs(self):
        for p in self.particles:
	    x = p.getX()
	    v = p.getV()
            for i in range(2):
                x[i] += v[i] 
	    #p.setX(x)

    def calVs(self):
        for i,p in enumerate(self.particles):
	    v = p.getV() 
            x = p.getX()
            BX = p.getBX()
            #print i,BX
            p.setV([v[0] + (self.alpha*self.Es[0]*(self.bestPos[0]-x[0])) + (self.beta*self.Es[1]*(BX[0]-x[0])) , v[1] + (self.alpha*self.Es[0]*(self.bestPos[1]-x[1])) + (self.beta*self.Es[1]*(BX[1]-x[1])) ])

    def calBestParticlePos(self):
        for p in self.particles:
            z = p.calZ(p.getX(),self.Goal,False)
            if z<=self.minZ:
                self.minZ = z
                self.bestPos = p.getX()

    def generateEs(self):
        e = []
        e.append(random.uniform(0.0,1.0))
        e.append(random.uniform(0.0,1.0))
        return e        

    def printRegion(self): #Draws the goal region
	self.region = canvas.create_oval(self.Goal[0]-self.halfsizeBP, self.Goal[1]-self.halfsizeBP, self.Goal[0]+self.halfsizeBP, self.Goal[1]+self.halfsizeBP, fill="green")
        

    #Generate a Position avoiding restricted areas
    def generatePos(self): 
        while True:
	    x = []
	    x.append(random.randint(0,anchotk-halfparti))
	    x.append(random.randint(0,altotk-halfparti))
            ex = False
            #avoiding retricted areas
            #Here can be added restricted areas and obstacles
            #for area in self.restrictedRespawnAreas:
            for area in self.obstaclesCoords:
                if not self.pointIsInArea(x,area):
                    ex = True
                    break
            if ex:
                break;
	return x[:]

    def pointIsInArea(self,x,area): #Check is a point is in a defined area
        if x[0]>area[0] and x[1]>area[1] and x[0]<area[2] and x[1]<area[3]:
            return True
        else:
            return False
    


class Particle:
    def __init__(self, x, goal):
	self.x = x #Particle position
	self.v = [random.randint(-1,1),random.randint(-1,1)] #V vector
	self.z,self.x1 = self.calZ(self.x,self.v,True) #Calculate module and next position
        self.active = True
	self.initial = True
	
        #For PSO calculations
        self.BestPos = self.x[:]
        self.minZ = 4000.0
	self.drawFigures(goal)
	self.move_active(goal)

    def posUpdate(self,goal):
	canvas.delete(self.shape) #Delete particle
	canvas.delete(self.arr) #Delete vector
	self.drawFigures(goal)

    def drawFigures(self,goal):
        notUsed,self.x1 = self.calZ(self.x, self.v, True)
	if not self.initial:
	    z = self.calZ(self.x, goal,False)
	    self.checkMinZ(z,self.x[:])
	else:
	    self.initial = False
	
	self.shape = canvas.create_oval(self.x[0]-halfparti, self.x[1]-halfparti, self.x[0]+halfparti, self.x[1]+halfparti, fill=color) #Circle particle drawing
        self.arr = canvas.create_line(self.x[0], self.x[1], self.x1[0], self.x1[1], arrow=LAST, fill = "red", arrowshape = (4,5,2)) #Arrow vector drawing
        
    #For calculate minimum module and save best position coords
    def checkMinZ(self,z,x): 
        if z<=self.minZ:
            self.minZ = z
            self.BestPos = x[:]

    def getBX(self):
        return self.BestPos[:]

    def calZ(self,x,v,Vel):
	if Vel:
	    x1 = [x[0]+v[0],x[1]+v[1]] #Arrow coords
	else:
	    x1 = v
	z = math.sqrt((x1[0]-x[0])**2+(x1[1]-x[1])**2) #Module

	if Vel:
	    return [z,x1[:]]
	else:
	    return z

    def getZ(self):
	return self.z[:]

    def getX(self):
	return self.x[:]

    def getV(self):
	return self.v[:]

    def setX(self,x):
	self.x = x[:]
    
    def setV(self,v):
	self.v = v[:]

    def move_active(self,goal):
        if self.active:
            self.posUpdate(goal)
	else:
	    canvas.delete(self.arr) #Delete vector





S = Simulation(particles)
tk.mainloop()
