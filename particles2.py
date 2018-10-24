try:
    # for Python2
    from Tkinter import *    
except ImportError:
    # for Python3
    from tkinter import *   

import random
import time
import math

global canvas

particles = 2
fps = 1
timing = 1000/fps
anchotk = 500
altotk = 500
partiSize = 8 #Tiene que ser un numero par
halfparti = partiSize/2
tk = Tk()
canvas = Canvas(tk, width=anchotk, height=altotk, bg="white")
canvas.pack()
color = 'black'

vbounds = 20

class Simulation:
    
    def __init__(self, np):
        #Class constants
        self.Goal= [400,400]
        self.sizeGoal = 40
        self.halfsizeBP = self.sizeGoal/2
        self.alpha = 0.5
        self.beta = 0.5
	self.np = np #number of particles
        self.restrictedRespawnAreas = [[300,300,anchotk,altotk]] 
	self.animate = False
	
	if self.animate:
	    self.bckpt = []
	    self.bckptp1 = []
	

        #Class variables
	self.particles = []
	for i in range(0,self.np): #respawn particles
	    self.particles.append(Particle(self.generatePos()))
        
        self.Es = self.generateEs()
        self.bestPPos = self.calBestParticlePos()
        
        
        #Print constant canvas objects
        self.printRegion()
        #Set refreshment loop
	self.updateParticles()

    def updateParticles(self):
        self.Es = self.generateEs()

	if self.animate:
	    self.bckpt = self.bckptp1[:] #For animation, shift future register to present register	
        self.calVs()
	self.calXs()

	if self.animate:
	    self.bckptp1 = self.storeVtXt() #for animation
	    self.animate()
	    self.resetVX() #Reset real values

        for p in self.particles: #print real movements
	   p.move_active()
        self.bestPPos = self.calBestParticlePos()
	tk.after(timing, self.updateParticles) 


    def animate(self):
        z = []
        for i,bb in enumerate(zip(self.bckpt[:],self.bckptp1[:])):
            #print bb
            b = bb[0]
            b2 = bb[1]
            x = b[0]
            xp1 = b2[0]
            temp = []
            temp.append(math.sqrt( ( (xp1[0]-x[0]) **2) + ( (xp1[1]-x[1]) **2) ) )
            #temp.append(math.sqrt((xp1[0]-x[0])**2 + (xp1[1]-x[1])**2))
            temp.append(i)

            z.append(temp)
        print "Zeta:"
        print z
        sorted(z)
        print "Sorted"
        print z


    def resetVX(self):
        for p,b in zip(self.particles,self.bckptp1[:]):
            p.setV(b[0])
            p.setX(b[1])

    def storeVtXt(self):
        data = []
        for p in self.particles:
            data.append([p.getV() , p.getX()])
	return data


    def calXs(self):
        for p in self.particles:
	    x = p.getX()
	    v = p.getV()
            i = 0
            x[i] += v[i] 
            i = 1
            x[i] += v[i]
	    p.setX(x)

    def calVs(self):
        for p in self.particles:
	    v = p.getV() 
            p.setV([v[0] + (self.alpha*self.Es[0]*(self.Goal[0]-p.x[0])) + (self.beta*self.Es[1]*(self.bestPPos[0]-p.x[0])) , v[1] + (self.alpha*self.Es[0]*(self.Goal[1]-p.x[1])) + (self.beta*self.Es[1]*(self.bestPPos[1]-p.x[1]))])

    def calBestParticlePos(self):
        minZ = 4000.0
        bestX = []
        for p in self.particles:
            z = math.sqrt((p.x[0]-self.Goal[0])**2 + (p.x[1]-self.Goal[1])**2)
            if z<minZ:
                minZ = z
                bestX = p.x

        print bestX
        return bestX

    def generateEs(self):
        e = []
        e.append(random.uniform(0.0,1.0))
        e.append(random.uniform(0.0,1.0))
        return e        

    def printRegion(self):
	self.region = canvas.create_oval(self.Goal[0]-self.halfsizeBP, self.Goal[1]-self.halfsizeBP, self.Goal[0]+self.halfsizeBP, self.Goal[1]+self.halfsizeBP, fill="green") #Dibuja la region
        

    def generatePos(self):
        while True:
            #Generate position
	    x = []
	    x.append(random.randint(0,anchotk-halfparti))
	    x.append(random.randint(0,altotk-halfparti))
            ex = False
            #avoiding retricted areas
            for area in self.restrictedRespawnAreas:
                #print area
                #print x
                #print self.pointIsInArea(x,area)
                if not self.pointIsInArea(x,area):
                    ex = True
                    break
            if ex:
                break;

        #print "x fue generada"
	return x[:]

    def pointIsInArea(self,x,area):
        if x[0]>area[0] and x[1]>area[1] and x[0]<area[2] and x[1]<area[3]:
            return True
        else:
            return False
    


class Particle:
    def __init__(self, x):
	self.x = x #Posicion de la particula
	self.v = [random.randint(-1,1),random.randint(-1,1)] #Vector v de la particula
	self.shape = canvas.create_oval(self.x[0]-halfparti, self.x[1]-halfparti, self.x[0]+halfparti, self.x[1]+halfparti, fill=color) #Dibuja el ovalo
        self.arr = canvas.create_line(self.x[0], self.x[1], self.x[0]+self.v[0], self.x[1]+self.v[1], arrow=LAST, fill = "red", arrowshape = (4,5,2) )
        self.active = True
        self.move_active()

    def posUpdate(self):
	canvas.delete(self.shape) #Borra particula
	canvas.delete(self.arr) #Borra vector de v

	self.shape = canvas.create_oval(self.x[0]-halfparti, self.x[1]-halfparti, self.x[0]+halfparti, self.x[1]+halfparti, fill=color) #Dibuja el ovalo
        self.arr = canvas.create_line(self.x[0], self.x[1], self.x[0]+self.v[0], self.x[1]+self.v[1], arrow=LAST, fill = "red", arrowshape = (4,5,2))



    def getX(self):
	return self.x[:]

    def getV(self):
	return self.v[:]

    def setX(self,x):
	self.x = x[:]
    
    def setV(self,v):
	self.v = v[:]

    def move_active(self):
        if self.active:
            self.posUpdate()




S = Simulation(particles)
tk.mainloop()
