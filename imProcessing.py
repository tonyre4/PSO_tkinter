#-* coding: utf8 -*-
def getObsCoordsPNG(nombre_imagen):
    import numpy as np
    import cv2
    imBGR = cv2.imread(nombre_imagen,1)
    im = cv2.cvtColor(imBGR, cv2.COLOR_BGR2GRAY)
    th, imbw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    imcon, conts, hier = cv2.findContours(imbw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    puntos = range(len(conts))

    #Muestra las áres, perimetros y centroides
    for x in puntos:
        #Para el centroide se requieren los momentos de masa
        M = cv2.moments(conts[x])
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        puntos[x] = [conts[x][0][0][0], conts[x][0][0][1], conts[x][2][0][0], conts[x][2][0][1]] ,[cx, cy]
        
    height, width, chan = imBGR.shape
    res = [width,height]

    return res,puntos
