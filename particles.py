from Tkinter import Canvas

try:
    # for Python2
    from Tkinter import *    
except ImportError:
    # for Python3
    from tkinter import *   

import sys
import random
import ParticlesClass
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
tk.title("Particulas")
canvas = Canvas(tk, width=anchotk*2, height=altotk, bg="white")  # type: Canvas #Canvas object
ParticlesClass.canvas = canvas
ParticlesClass.halfparti = halfparti
canvas.pack()

debug = True


#Parse arguments
try:
    print args[1]
    print type(args[1])
    if args[1].find(".png")>-1:
        import imProcessing
        byFile = False
	R,OBS = imProcessing.getObsCoordsPNG(args[1])
	#Mapping coords
	obss=[]
	for o in OBS:
	    t = []
	    t.append(int(anchotk*o[0][0]/R[0]))
	    t.append(int(altotk*o[0][1]/R[1]))
	    t.append(int(anchotk*o[0][2]/R[0]))
	    t.append(int(altotk*o[0][3]/R[1]))
	    obss.append(t[:])

    elif args[1].find(".coords")>-1:
        fileobs = args[1]
	byfile = True
    else:
	raise IndexError
except:
    print "Se necesita como primer argumento la entrada de los obstaculos, puede ser un archivo .coords o un archivo PNG para ser procesado."
    exit()


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
	if byFile:
	    self.readObstacles() #function that reads obstacles file
        else:
            self.obstaclesCoords = obss
	self.printObstacles() #This function will print obstacles once
        self.printGoal() #This print area goal
        self.generateParticles()# Generates all particles
        self.calcBestGlobal() #Calculating initial g*
        self.setBinds()

        self.velMap()
        self.drawVRepr()
        self.printRightLine()
        self.printBounds()
        #exit()

        #Loop execution
        self.loop()

        #######################################################
        #Calculation constant methods (they only will run once)
    
    #It generate all particles and store them
    def generateParticles(self):
        for i in range(0,self.np): #respawn particles
            self.particles.append(ParticlesClass.Particle(self.generatePos(),i,self.Goal))
    
    #reads .coords from input
    def readObstacles(self):
        with open(fileobs,"r") as f: #Reading file
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
    def printRightLine(self):
        RL = canvas.create_line(anchotk,0,anchotk,altotk)
        return

    def printBounds(self):
        for y in range(0,altotk,100):
            x = y
            canvas.create_line(anchotk, y+50, anchotk*2, y+50, width=1, fill="red")
            canvas.create_line(anchotk, y, anchotk*2, y, width=1, fill="gray")
            canvas.create_line(anchotk+x+50, 0, anchotk+x+50, altotk, width=1, fill= "red")
            canvas.create_line(anchotk+x, 0, anchotk+x, altotk, width=1, fill="gray")
            canvas.create_text(anchotk+10, y+10, text=str(y), fill="gray")
            canvas.create_text(anchotk+10+x, 10, text=str(x), fill="gray")


    def printObstacles(self):
        for obs in self.obstaclesCoords:
            self.obstacles.append(canvas.create_rectangle(obs[0], obs[1], obs[2], obs[3], fill = 'orange'))
    
    def printGoal(self): #Draws the goal region
        ag = self.areaGoal
        self.region = canvas.create_oval(ag[0], ag[1], ag[2], ag[3], fill="green")

    def drawVRepr(self):
        for y in range(altotk):
            for x in range(anchotk):
                print self.vMap[y][x][1]
                if self.vMap[y][x][1] == -1.0:
                    cl = "black"
                elif self.vMap[y][x][1] > 0 and self.vMap[y][x][0] == 0:
                    cl = "red"
                elif self.vMap[y][x][0] == 90:
                    cl = "green"
                elif self.vMap[y][x][0] == 180:
                    cl = "cyan"
                elif self.vMap[y][x][0] == -90:
                    cl = "purple"
                else:
                    cl = "white"

                canvas.create_line(x+anchotk, y, x+1+anchotk, y, width=0, fill=cl)

    def velMap(self):
        #making velocities mapping
        ###############angle,magnitude
        self.vMap = [[[    0,      0.0]for k in range(anchotk)] for l in range(altotk)]

        #size of the kernel
        self.kernel = 3
        k = self.kernel
        #How much kernels will build
        self.layers = 2
        l = self.layers

        #modifiying it through obstacles
        #using horizontal axis as reference (to right)
        for o in self.obstaclesCoords:
            #for each left line of obstacles
            ang = -90 #down direction
            #it also include the next layers times the kernel until down
            for y in range(o[1],o[3]+(l*k)):
                for la in range(l):
                    for x in range(o[0]-((la+1)*k),o[0]-(la*k)):
                        try:
                            if y >= 0 and x >= 0:
                                #a = self.vMap[y][x][0]
                                m = self.vMap[y][x][1]
                                self.vMap[y][x] = [ang,m+(1.0/(1+la))] #with magnitude decreasing each layer
                        except:
                            print "Out of bounds: " ,y ,x

        #Now in up direction of right side of every obstacle
        for o in self.obstaclesCoords:
            #for each left line of obstacles
            ang = 90 #up direction
            #it also include the next layers times the kernel until up
            for y in range(o[1]-(l*k),o[3]):
                for la in range(l):
                    for x in range(o[2]+(la*k),o[2]+((la+1)*k)):
                        try:
                            if y >= 0 and x >= 0:
                                a = self.vMap[y][x][0]
                                m = self.vMap[y][x][1]
                                self.vMap[y][x] = [ang,m+(1.0/(1+la))] #with magnitude decreasing each layer
                        except:
                            print "Out of bounds: " , y, x


            # # Now in right direction of bottom side of every obstacle
            for o in self.obstaclesCoords:
                # for each bottom line of obstacles
                ang = 0  # right direction
                # it also include the next layers times the kernel until up
                for la in range(l):
                    for y in range(o[3]+(la*k), o[3]+((la+1)*k)):
                        for x in range(o[0] , o[2] + ((l * k))):
                            try:
                                if y >= 0 and x >= 0:
                                    a = self.vMap[y][x][0]
                                    m = self.vMap[y][x][1]
                                    self.vMap[y][x] = [ang,
                                                       m + (1.0 / (1 + la))]  # with magnitude decreasing each layer
                            except:
                                print "Out of bounds: ", y, x

            # # Now in right direction of bottom side of every obstacle
            for o in self.obstaclesCoords:
                # for each top line of obstacles
                ang = 180  # left direction
                # it also include the next layers times the kernel until up
                for la in range(l):
                    for y in range(o[1]-((la+1)*k), o[1]-(la*k)):
                        for x in range(o[0]-(l*k) , o[2]):
                            try:
                                if y >= 0 and x >= 0:
                                    a = self.vMap[y][x][0]
                                    m = self.vMap[y][x][1]
                                    self.vMap[y][x] = [ang,
                                                       m + (1.0 / (l - la))]  # with magnitude decreasing each layer
                            except:
                                print "Out of bounds: ", y, x

        #all coords with magnitude = -1 are not allowed to reach the particle
        for o in self.obstaclesCoords:
            for y in range(o[1],o[3]):
                for x in range(o[0],o[2]):
                    self.vMap[y][x] = [0,-1.0]

        if debug:
            #printing coords in file (debug)
            with open("vmap.txt", "w+") as f:
                for l in self.vMap:
                    f.write(str(l) + "\n")
            with open("vmap1.txt", "w+") as f:
                for y in range(60):
                    for x in range(60):
                        f.write(str(self.vMap[y][x]) + ",\t")
                    f.write("\n")

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

    def hitAObstacle(self, x, P):
        for a in self.obstaclesCoords:
            try:
                if self.vMap[int(x[1])][int(x[0])][1] == -1.0:
                    if debug and P:
                        print "HIT:"
                        print "By vMap Input: ", x
                    return True
            except:
                pass
            if self.pointIsInArea(x, a):
                if debug and P:
                    print "HIT:"
                    print "Hitting obstacle coords: " , a, "Input Coords: ", x
                return True
        return False

    # def intersects(self,x,v):
    #     V100 = [v[i]/100.0 for i in range(2)]
    #     for j in range(100):
    #         xh = [x[i] + (j*V100[i]) for i in range(2)]
    #         if self.hitAObstacle(xh):
    #             return True
    #     return False

    def intersects2(self, xi, xf):
        X100 = [(xf[i]-xi[i])/100.0 for i in range(2)]
        for j in range(100):
            xh = [math.floor(xi[i] + (j*X100[i])) for i in range(2)]
            if self.hitAObstacle(xh, False):
                if debug:
                    print "INTERSECTS:"
                    print "Intesection Coords: ", xh
                return True
        return False

    def calcBestGlobal(self): #Calculates g*
        if self.calculateBPP:
            ps = self.particles
            g = self.Goal
            mini = self.calcModule(ps[0].getX(),g)
            index = 0

            for i in range(1,len(ps)): #Calculates all modules
                mz = self.calcModule(ps[i].getX(),g)
                if mz<mini:
                    mini = mz
                    index = i
                if not ps[i].isActivated():
                    self.calculateBPP = False
            self.BPP = ps[index].getX() #stores best g*


    def calcModule(self,x,y): #Calculates module from x to y
        z = math.sqrt( (y[0]-x[0])**2 + (y[1]-x[1])**2 )
        return z

    def calcAngle(self,x,y):
        ang = math.tan()
        return ang

    def generateEs(self): #Generates E random numbers
        e = [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]
        return e

    def calcV(self,x,xa,v):
        a = self.alpha
        b = self.beta
        e = self.E
        g = self.BPP

        V = [v[i]+(a*e[0]*(g[i]-x[i]))+(b*e[1]*(xa[i]-x[i])) for i in range(2)]
        return V

    def calcX(self, x, v):
        return [x[i]+v[i] for i in range(2)]

    def deg2rad(self,angle):
        return ((angle*math.pi)/180)
    
    def rotateVector(self,angle,x):
        theta = self.deg2rad(angle)
        cs = math.cos(theta)
        sn = math.sin(theta)
        return [x[0]*cs - x[1]*sn , x[0]*sn + x[1]*cs]

    ############
    #Loop method
    def loop(self):
        for p in self.particles:
            #self.E = self.generateEs()
            p.setV(self.calcV(p.getX(),p.getBX(),p.getV()))#generate new velocity t+1
            fx = self.calcX(p.getX(),p.getV())
            p.setArr(fx) #Estimated new point
            p.move_active() #draw particle again
            #if not self.pointIsInArea(fx,[0,0,anchotk,altotk]) or self.hitAObstacle(fx) or (self.intersects(p.getX(),p.getV())):
            if not self.pointIsInArea(fx,[0,0,altotk,anchotk]) or self.hitAObstacle(fx,False) or (self.intersects2(p.getX(),fx)):

                ##DEBUG
                if debug:
                    print "Particle " , p.getIndex(), ": "
                    if not self.pointIsInArea(fx,[0,0,anchotk,altotk]):
                        print "Out of drawing Area"
                    if self.hitAObstacle(fx,True):
                        print "Is hitting an obstacle. PCoords: " , p.getX() , "PVel: " , p.getV()
                    elif self.intersects2(p.getX(),fx):
                        print "Is intersecting an obstacle. PCoords: " , p.getX() , "PVel: " , p.getV()
                    #raw_input();

                x = p.getX()
                try:
                    print x
                    ang,mag=self.vMap[int(x[1])][int(x[0])]
                except:
                    mag = 0

                if mag==0: #if there is no magnitude, just provide a random velocity
                    randV = [random.randint(-1,1),random.randint(-1,1)]
                    randV2 = [random.randint(-50,50),random.randint(-50,50)]
                    v = p.getV()
                    p.setV([v[i]*randV[i] + randV2[i] for i in range(2)])
                else: #if not, calculate new velocity and position
                    #x = [x[i] for i in range(2)]
                    ztemp = self.calcModule(x, fx)
                    if ztemp > 200:
                        ztemp /= -2
                    xi = x
                    if ang == 0:
                        x = [x[0]+ztemp, x[1]]
                        p.setV([ztemp, 0.0])
                    elif ang == 90:
                        x = [x[0], x[1]+ztemp]
                        p.setV([0.0, ztemp])
                    elif ang == -90:
                        x = [x[0], x[1]-ztemp]
                        p.setV([0.0, -ztemp])
                    elif ang == 180:
                        x = [x[0]-ztemp, x[1]]
                        p.setV([-ztemp, 0.0])

                    tri = 0
                    rev = 1
                    revx = 1
                    onx = 0
                    while (not self.pointIsInArea(x,[0,0,altotk,anchotk]) or self.hitAObstacle(x,False) or (self.intersects2(p.getX(),x))):
                        if tri>100:
                            x = xi
                            vvv = p.getV()
                            p.setV([-1*vvv[i] for i in range(2)])
                            break
                            if rev == -1:
                                onx = 1
                            rev *=-1
                            tri = 0
                            ztemp*=10

                        ztemp /=2
                        r1 = random.randint(-1,1)
                        r2 = random.randint(0,5)
                        noise = onx*r1*r2

                        if ang == 0:
                            x = [(xi[0]+ztemp)*rev, xi[1]+noise]
                        elif ang == 90:
                            x = [xi[0]+noise, rev*(x[1]+ztemp)]
                        elif ang == -90:
                            x = [xi[0]+noise, rev*(xi[1]-ztemp)]
                        elif ang == 180:
                            x = [rev*(xi[0]-ztemp), xi[1]+noise]
                        tri+=1
                        print "Calculating..."

                    p.setX(x)


            else:
                p.setX(fx)#generate new positions t+1

            p.setArr(p.calcArrowPoint())
            p.calcBx()#calculate x*
            p.move_active()
            if self.pointIsInArea(p.getX(),self.areaGoal):
                p.deactivateParticle()
            self.calcBestGlobal()#Find current g*

        tk.after(500, self.loop)



S = Simulation(particles)

tk.mainloop()
