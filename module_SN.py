# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 09:25:27 2017

@author: isaac
"""

import gpxpy
import gpxpy.gpx
import math
import numpy  as np


r = 0.05


def anguloRectasVdir(rx1, ry1, rx2, ry2, rx3, ry3, threshold):
    vx1 = rx2 - rx1
    vy1 = ry2 - ry1

    vx2 = rx3 - rx2
    vy2 = ry3 - ry2

    numerador = ((vx1 * vx2) + (vy1 * vy2))
    deno = math.sqrt(math.pow(vx1, 2) + math.pow(vy1, 2)) * math.sqrt(math.pow(vx2, 2) + math.pow(vy2, 2))

    if deno == 0: return False
    angulo = math.degrees(math.acos(numerador / deno))

    if numerador < 0 and angulo > threshold:
        return True
    return False


def distance(longitude, latitude, longitude1, latitude1):
    return math.sqrt(math.pow(longitude1 - longitude, 2) + math.pow(latitude1 - latitude, 2))


def drange(start, stop, step):
    r = start
    if r > stop:
        while r < stop:
            yield r
            r -= step
    if r < stop:
        while r < stop:
            yield r
            r += step


# TOOD:  WARNING: cuando la pendiente sea 90g. no devolvera ningun punto intermedio
#  Se puede optimizar reduciendo el numero de puntos:
#  drange(x1,x2,r*2) 2-diametro; 3-4-5-6...
#
def rectaInterPolacionCircles(x1, y1, x2, y2, r):
    vx = x2 - x1
    vy = y2 - y1

    if vx == 0:
        m = 10
    else:
        m = vy / vx


    # En caso de que la recta tenga mucha pendiente
    # Se reduce el step
    if m > 3.5:
        r = r / 3

    # Ordenamos el sentido correcto del rango de puntos
    if vx < 0:
        rango = drange(x2, x1, r * 2)
    else:
        rango = drange(x1, x2, r * 2)

    # y = []
    # x = []
    points = []
    # Se calculan la cantidad de puntos intermedios donde se pondra un circulo
    for px in rango:
        varY = (m * (px - x1)) + y1
        # y.append(varY)
        # x.append(px)
        points.append([px,varY])


    # return OrderedDict({"x": x, "y": y})
    return sorted(points)

# r radius
# d = L - E ( Direction vector of ray, from start to end )
# f = E - C ( Vector from center sphere to ray start )
# cx cy center circle
# lx1,y1 ---> lx2,y2
def HayInterseccion(R, Ax, Ay, Bx, By, Cx, Cy):
    LAB = math.sqrt(math.pow(Bx - Ax, 2) + math.pow(By - Ay, 2))

    if LAB == 0:
        return False

    # compute the direction vector D from A to B
    Dx = (Bx - Ax) / LAB
    Dy = (By - Ay) / LAB

    # Now the line equation is x = Dx*t + Ax, y = Dy*t + Ay with 0 <= t <= 1.
    #  compute the value t of the closest point to the circle center (Cx, Cy)
    t = Dx * (Cx - Ax) + Dy * (Cy - Ay)

    # This is the projection of C on the line from A to B.
    # compute the coordinates of the point E on line and closest to C
    Ex = t * Dx + Ax
    Ey = t * Dy + Ay

    # compute the euclidean distance from E to C
    LEC = math.sqrt(math.pow(Ex - Cx, 2) + math.pow(Ey - Cy, 2))

    # test if the line intersects the circle
    # Si R == LEC - recta tangencial
    if LEC >= R:
        return False
    if LEC < R:
        # Hay una interseccion con la recta
        dt = math.sqrt(math.pow(R, 2) - math.pow(LEC, 2))

        # compute first intersection point
        Fx = (t - dt) * Dx + Ax
        Fy = (t - dt) * Dy + Ay

        # compute second intersection point
        Gx = (t + dt) * Dx + Ax
        Gy = (t + dt) * Dy + Ay

        # print "\t\t\t F(%f,%f) " %(Fx,Fy)
        # print "\t\t\t G(%f,%f) " %(Gx,Gy)
        # Algunos de los puntos esta dentro de ese rango-recta
        if (Bx >= Fx >= Ax or Ax >= Fx >= Bx or Bx >= Gx >= Ax or Ax >= Gx >= Bx) and \
                (By >= Fy >= Ay or Ay >= Fy >= By or By >= Gy >= Ay or Ay >= Gy >= By):
            return True
        return False


def getSimpleNodes2(file):
#    file = pathDst+str(6657107)+".gpx"
    coordR = []
    nodesB =[]
    nodesIndex = []
    valuesInterpolation = []
    intersecction  = []
    #  Primero se calcula las intersecciones posibles con una version simplificada del track
    with open(file, 'r') as f:
        p = gpxpy.parse(f)
        p.simplify()
#        p.reduce_points(20)
        lenPoints = 0
        for track in p.tracks:  # OJO SOLO HAY UN TRACK
            for segment in track.segments:  # OJO SOLO HAY UN SEGMENT
                lenPoints = len(segment.points)
                for iA in range(0,len(segment.points)-1):
                    coordR.append([segment.points[iA].longitude,segment.points[iA].latitude])
#                    print iA
                    A = segment.points[iA]
                    if iA+1 < lenPoints:
                        B = segment.points[iA+1]
#                        listPoints = rectaInterPolacionCircles(A.longitude,A.latitude,B.longitude,B.latitude,0.002)
                        listPoints = rectaInterPolacionCircles(A.longitude,A.latitude,B.longitude,B.latitude,0.002)
                        valuesInterpolation.append(listPoints)

                        for center in listPoints:

                            minR = len(segment.points)-1
                            maxR = iA+2
                            step = -1
                            for iJ in range(minR,maxR,step):
                                C = segment.points[iJ]
                                if iJ-1>=0:
                                    D = segment.points[iJ-1]
                                    if HayInterseccion(0.0004,C.longitude,C.latitude,D.longitude,D.latitude,center[0],center[1]):
                                        intersecction.append(center)
                                        nodesIndex.append([iA,iJ])
                            #endFor
                        #endFor
                #endFor -points
            #endFor  - segement
        #endFor - track

    

    threshold = int(lenPoints*0.06)
    thresholdX = 2

    if len(nodesIndex)>0:
        minX = nodesIndex[0][0]
        minXTMP = minX
        minY = nodesIndex[0][1]
        tried = True

        for i in range(1,len(nodesIndex)):
            item = nodesIndex[i]
            if minXTMP+threshold <= item[0]:
                if (nodesIndex[i][1]-nodesIndex[i][0]>threshold):
                    nodesB.append(intersecction[i])
                if (nodesIndex[i-1][1]-nodesIndex[i-1][0]>threshold):
                    nodesB.append(intersecction[i-1])
                else:
                    try:
                        if (nodesIndex[i-2][1]-nodesIndex[i-2][0]>threshold)\
                                and (minXTMP-nodesIndex[i-2][0] < thresholdX):
                            nodesB.append(intersecction[i-2])
                    except:
                        None
                minX = item[0]
                minXTMP = minX
                minY = item[1]
            else:
                tried = False
                if minY>item[1]:
                    minY = item[1]
                if minXTMP+thresholdX >= item[0]:
                    minXTMP = item[0]
        #end for
        if len(nodesB)==0 and not tried:
           nodesB.append(intersecction[len(intersecction)-1])
    #end if


    nodesB.append([segment.points[0].longitude,segment.points[0].latitude])


    descartado= []
    if len(nodesB)>2:
        radius = 0.001    
        for i in range(0,len(nodesB)):
            center = nodesB[i]
            for j in range(i+1,len(nodesB)):
                point = nodesB[j]
                if (math.pow((point[1]-center[1]),2) +
                        math.pow((point[0] - center[0]),2)) < math.pow(radius,2):
                    descartado.append(nodesB[j])

    nodesB.append([segment.points[len(segment.points)-1].longitude,segment.points[len(segment.points)-1].latitude])
    
    #Se genera una nueva lista con los puntos no descartados
    realNodes = [item for item in nodesB if item not in descartado]

    #==============================================================================
    # Special route: a long line
    #==============================================================================
    if len(realNodes)==1:
         realNodes.append([segment.points[0].longitude,segment.points[0].latitude])
         realNodes = np.array(realNodes)
         realNodes = realNodes[::-1]

    return realNodes,intersecction,valuesInterpolation,coordR


#==============================================================================
# Some codes
# INPUT FILES SHOULD BE IMPORTED FROM GLOBALSTORAGE
#==============================================================================
def computeSN(job,options):
    job.fileStore.logToMaster("Starting COMPUTING SN")#    print options#routePath,pathGPX,pathOutFile):
    coords = {}
    
    rutas = np.load(options.pathNPY)

    for codeRoute in rutas:
        try:
#            print "Code: %i"%codeRoute
            nodes,intersecction,puntosInterpolation,coordR = getSimpleNodes2(options.pathGPX+str(codeRoute)+".gpx")
            assert len(nodes)>=2
          
            coords[codeRoute] = []
            coordsT = np.array(nodes)
            coordsT[0]=nodes[-2]
            coordsT[-1]=nodes[-1]
            for idx in range(0,len(nodes)-2):
                coordsT[idx+1]=nodes[len(nodes)-(3+idx)]    
            coords[codeRoute] = coordsT
   
        except:
            print "No file:"
            continue
      
    #Building CSV format for Fusion-job
    coordF = []
    for route in coords:
        for c in coords[route]:
            coordF.append(list(np.concatenate((c,[route]))))
    coordF = np.array(coordF)
    
#    np.savetxt(pathOutFile,coordF,delimiter=",")
    with job.fileStore.writeGlobalFileStream() as (fileHandle, outComputeSNID):
        np.savetxt(fileHandle,coordF,delimiter=",")        
    job.fileStore.exportFile(outComputeSNID, 'file:///Users/isaac/IdeaProjects/Network_Workflow/SNnodes.csv')

    job.fileStore.logToMaster("END SN")

#def computeSN(job,options):
#    job.fileStore.logToMaster("Starting COMPUTING SN")
#    npyFile = options.pathNPY 
#    codes = np.load(npyFile)
#    for code in codes:
#        job.fileStore.logToMaster("code file: %s"%code)
#
#    testWrite = np.array([0,2,1,3,543,45,2])
#
#    with job.fileStore.writeGlobalFileStream() as (fileHandle, outComputeSNID):
#        np.save(fileHandle,testWrite)        
#
#    job.fileStore.exportFile(outComputeSNID, 'file:///Users/isaac/IdeaProjects/Network_Workflow/SNnodes.npy')

