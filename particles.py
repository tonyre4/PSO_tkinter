try:
    # for Python2
    from Tkinter import *    
except ImportError:
    # for Python3
    from tkinter import *   

import random
import time

global canvas

particles = 100
fps = 20
timing = 1000/fps
anchotk = 500
altotk = 500
partiSize = 4 #Tiene que ser un numero par
halfparti = partiSize/2
tk = Tk()
canvas = Canvas(tk, width=anchotk, height=altotk, bg="white")
canvas.pack()
color = 'black'

vbounds = 10

class Simulation:
    
    def __init__(self, np):
	self.np = np #number of particles
	self.particles = []
	for i in range(0,np):
	    self.particles.append(Particle(self.generatePos()))
        
	self.updateParticles()

    def updateParticles(self):
	for p in self.particles:
	   p.move_active() 
	tk.after(timing, self.updateParticles) 
	    

    def generatePos(self):
	x = []
	x.append(random.randint(0,anchotk-halfparti))
	x.append(random.randint(0,altotk-halfparti))
	return x

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

        pos = canvas.coords(self.shape) #Lee coordenadas del ovalo

	self.x = [self.x[i]+self.v[i] for i in range(len(self.x))]

	if pos[0] < 0 and self.v[0]<0: 
            self.v[0] *= -1
	elif pos[2] > anchotk and self.v[0]>0: 
            self.v[0] *= -1
	if pos[1] < 0 and self.v[1]<0: 
            self.v[1] *= -1
	elif pos[3] > altotk  and self.v[1]>0: 
            self.v[1] *= -1

	self.randvels()

    def randvels(self): #para generar vels random
	z = self.v
	self.v = []
	if z[0]>0:
	    self.v.append(random.randint(1,vbounds))
	else:
	    self.v.append(random.randint(vbounds*-1,-1))
	if z[1]>0:
	    self.v.append(random.randint(1,vbounds))
	else:
	    self.v.append(random.randint(vbounds*-1,-1))


    def move_active(self):
        if self.active:
            self.posUpdate()



S = Simulation(particles)
tk.mainloop()
