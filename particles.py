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

#System constants
args = sys.argv
#Timing constants
particles = 10
fps = 60
timing = 1000/fps
slowness = 1
#Graphics constants
anchotk = 500
altotk = 500
partiSize = 8 #Size of paritcle #should be pair number
halfparti = partiSize/2
tk = Tk() #tk object
canvas = Canvas(tk, width=anchotk, height=altotk, bg="white") #Canvas object
canvas.pack() 
color = 'gray'


class Simulation:
    
    def __init__(self, np):
        ##########
	#Constants
	#Environment constants
        self.Goal= [400,400] #Goal coords
        self.sizeGoal = 40 #Size of the goal point
        self.halfsizeBP = self.sizeGoal/2 #half size of the goal point
	self.areaGoal = [self.Goal[0]-self.halfsizeBP, self.Goal[1]-self.halfsizeBP, self.Goal[0]+self.halfsizeBP, self.Goal[1]+self.halfsizeBP] #Area goal
	self.np = np #number of particles
        self.avoidRespawnAreas = False #For avoiding some areas to respawn
        
	#PSO constants
	self.alpha = 0.2 #learning coef
        self.beta = 0.2 #learning coef
        
	#Graphics constants
	self.restrictedRespawnAreas = [[300,300,anchotk,altotk]] #All restricted areas to respawn (this can be taken out)
        self.obstaclesCoords = [] #where areas coords of all obstacles will be stored
        self.obstacles = [] #where obstacle objects will be stored
       
	#Animation constants
	self.animate = True #if true animation will be created
	
	##########
	#Variables
	#Environment variables
	self.particles = [] #where particle objects will be stored
	self.BPP = [] #where Best Particle Position will be stored  <- g*

	#PSO variables
	self.E = self.generateEs()
	self.calculateBPP = True

	#Animation variables
	if self.animate:
	    self.frame = 0 #counting frames
	    self.Vparts = [] #to store parts of velocities

	##########################
	#Initial methods execution
	self.readObstacles() #function that reads obstacles file
        self.printObstacles() #This function will print obstacles once
	self.printGoal() #This print area goal
	self.generateParticles()# Generates all particles
	self.calcBestGlobal() #Calculating initial g*
	self.setBinds()

	#Loop execution
	self.loop()

    #######################################################
    #Calculation constant methods (they only will run once)
    
    #It generate all particles and store them
    def generateParticles(self):
	for i in range(0,self.np): #respawn particles
	    self.particles.append(Particle(self.generatePos(),i,self.Goal))
    
    #reads .coords from input
    def readObstacles(self):
        with open(args[1],"r") as f: #Reading file
            for l in f:
                l = l.replace("\n","")
                l = l.split(",")
                obs = []
                for coord in l:
                    obs.append(int(coord))
                self.obstaclesCoords.append(obs)
        print "Obstacles Coords:\n",self.obstaclesCoords
    
    #Generate a Position avoiding obstacles
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
                if self.pointIsInArea(x,area):
                    break
	    else:
		break
	return x[:]

    

    ###############################################
    #Graphics constant methods (they only run once)
    def printObstacles(self):
        for obs in self.obstaclesCoords:
            self.obstacles.append(canvas.create_rectangle(obs[0], obs[1], obs[2], obs[3], fill = 'orange'))
    
    def printGoal(self): #Draws the goal region
	ag = self.areaGoal
	self.region = canvas.create_oval(ag[0], ag[1], ag[2], ag[3], fill="green") 
    
    #################
    ##Binds for debug
    def setBinds(self):
	canvas.bind("<Button 1>", self.clickCoords)
	canvas.bind("<Button 2>", self.returnCoords)
	self.points = [] #to store points
	
    def clickCoords(self,event):
	self.points.append(event.x)
	self.points.append(event.y)
	print event.x , "," , event.y
	
    def returnCoords(self,event):
	for p in self.points:
	    print p,",",
	self.points = []


    ################
    #Dinamic methods
    def pointIsInArea(self,x,area): #Check is a point is in a defined area
        if x[0]>area[0] and x[1]>area[1] and x[0]<area[2] and x[1]<area[3]:
            return True
        else:
            return False

    def hitAObstacle(self,x):
	for a in self.obstaclesCoords:
	    if self.pointIsInArea(x,a):
		return True
	return False

    def intersects(self,x,v):
	V100 = [v[i]/100.0 for i in range(2)]
	for j in range(100):
	    xh = [x[i] + (j*V100[i]) for i in range(2)]
	    if self.hitAObstacle(xh):
		return True
	return False
    
    def calcBestGlobal(self): #Calculates g*
	if self.calculateBPP:
	    ps = self.particles
	    g = self.Goal
	    mini = self.calcModule(ps[0].getX(),g)
	    index = 0
	    #print index
	    #print mini

	    for i in range(1,len(ps)): #Calculates all modules
		mz = self.calcModule(ps[i].getX(),g)
		#print i 
		#print mz
		if mz<mini:
		    mini = mz
		    index = i
		    if not ps[i].isActivated():
			self.calculateBPP = False
	    #print "Best:"
	    #print index
	    #print mini
	    self.BPP = ps[index].getX() #stores best g*
	    #print self.BPP
	    
    def calcModule(self,x,y): #Calculates module from x to y
	z = math.sqrt( (y[0]-x[0])**2 + (y[1]-x[1])**2 )
	return z

    def generateEs(self): #Generates E random numbers
        e = []
        e.append(random.uniform(0.0,1.0))
        e.append(random.uniform(0.0,1.0))
        return e 

    def calcV(self,x,xa,v):
	a = self.alpha
	b = self.beta
	e = self.E
	g = self.BPP

	V = [v[i]+(a*e[0]*(g[i]-x[i]))+(b*e[1]*(xa[i]-x[i]))  for i in range(2)]
	return V

    def calcX(self,x,v):
	return [x[i]+v[i] for i in range(2)]

    ############
    #Loop method
    def loop(self):
	for p in self.particles:
	    self.E = self.generateEs()
	    p.setV(self.calcV(p.getX(),p.getBX(),p.getV()))#generate new velocity t+1
	    fx = self.calcX(p.getX(),p.getV())
	    if not self.pointIsInArea(fx,[0,0,anchotk,altotk]) or self.hitAObstacle(fx) or (self.intersects(p.getX(),p.getV())):
		randV = [random.randint(-1,1),random.randint(-1,1)]
		randV2 = [random.randint(-50,50),random.randint(-50,50)]
		v = p.getV()
		p.setV([v[i]*randV[i] + randV2[i] for i in range(2)])
	    else:
		p.setX(fx)#generate new positions t+1
	    p.setArr(p.calcArrowPoint())
	    p.calcBx()#calculate x*
	    p.move_active()
	    if self.pointIsInArea(p.getX(),self.areaGoal):
		p.deactivateParticle()
	self.calcBestGlobal()#Find current g*

	tk.after(500, self.loop)
	
    

class Particle:
    def __init__(self, x,index, goal):
	self.x = x #Particle position
	self.v = [random.randint(-1,1),random.randint(-1,1)] #velocity vector (first time is calculated randomly)
	self.index = index
	self.arrP = self.calcArrowPoint()
	self.goal = goal #this store goal position for multiple calculations
        self.active = True #for active movement
	
        #For PSO calculations
        self.BestPos = self.x[:]  #best position at begining is the x init position
        self.minZ = self.calcGoalModule() #minimum module is from current pos to goal
	self.drawParticle()
    
    #####################
    #calculations methods
    def calcGoalModule(self): #Calculates module from current x to goal
	x = self.x
	g = self.goal
	z = math.sqrt( (g[0]-x[0])**2 + (g[1]-x[0])**2 )
	return z
    def calcArrowPoint(self): #Calcultes arrow point to draw
	x = self.x
	v = self.v
	arr = []
	arr.append(x[0]+v[0])
	arr.append(x[1]+v[1])
	return arr[:]
    def calcBx(self): #Calculates x*
	mz = self.minZ
	cGM = self.calcGoalModule()
	if cGM < mz:
	    self.minZ = cGM
	    self.BestPos = self.x[:]

    ########################
    #All get and set methods
    def getBX(self): #to get best positon of the particle that it has touched
        return self.BestPos[:]
    def getX(self): #To get position vector
	return self.x[:]
    def getV(self): #To get Velocity vector
	return self.v[:]
    def setX(self,x): #To set position
	self.x = x[:]
    def setV(self,v): #To set Velocity
	self.v = v[:]
    def setArr(self,a):
	self.arrP = a[:]
    def isActivated(self):
	return self.active

    #################
    #Graphics methods
    def move_active(self): #Movement 
        if self.active: #if the particle is active
            self.drawParticle() #The particle will be drawn
    def deactivateParticle(self):
	canvas.delete(self.arr) #Delete arrow drawing
	self.active = False
    def drawParticle(self):
	self.calcArrowPoint()
	x = self.x
	a = self.arrP
	#deleting objects from canvas
	try:
	    canvas.delete(self.shape) #Delete particle
	    canvas.delete(self.arr) #Delete vector
	    canvas.delete(self.text)
	except:
	    pass
	#drawing particle and arrow
	self.text = canvas.create_text(x[0],x[1]-15,text=str(self.index))
	self.shape = canvas.create_oval(x[0]-halfparti, x[1]-halfparti, x[0]+halfparti, x[1]+halfparti, fill=color) #Circle particle drawing
        self.arr = canvas.create_line(x[0], x[1], a[0], a[1], arrow=LAST, fill = "red", arrowshape = (4,5,2)) #Arrow vector drawing
        


S = Simulation(particles)

tk.mainloop()
