# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:22:45 2017

@author: isaac
"""

__author__ = 'isaac'

#GENERA UN NUEVO FICHERO CON LOS NODOS entre SINGLE Y DOUBLE
#

import gpxpy
import numpy as np
from geopy.distance import vincenty

pathFile = "cimasData/Massanella/"


def joinSNIN(job,option):


    sortFileID = job.fileStore.importFile('file:///Users/isaac/IdeaProjects/Network_Workflow/SNnodes.csv')
    with job.fileStore.readGlobalFileStream(sortFileID) as fH:
        coordsSN = np.loadtxt(fH,delimiter=",",usecols=(0,1,2))

    sortFileID2 = job.fileStore.importFile('file:///Users/isaac/IdeaProjects/Network_Workflow/INnodes.csv')
    with job.fileStore.readGlobalFileStream(sortFileID2) as fH2:
        coordsIN = np.loadtxt(fH2,delimiter=",",usecols=(0,1,2,3))        
        
    routes = np.unique(coordsIN[:,2]).astype(int)
    tolerance = 100.0

    sort_routes = []

    for route in routes:
#            print "SN Route: %i" %route
            routeCoordsSN = coordsSN[coordsSN[:,2]==route]
            routeCoordsIn = coordsIN[coordsIN[:,2]==route]
            routeCoordsIn2 = coordsIN[coordsIN[:,3]==route]
           
#            assert len(routeCoordsSN)<2
    
            sort_coords = []    
            sort_coords.append(routeCoordsSN[0][0:3].tolist())   
            coords = np.concatenate((routeCoordsSN[1:-1],routeCoordsIn[:,0:3],routeCoordsIn2[:,0:3]))

            if len(coords) == 1:
                sort_coords.append(coords[0][0:3])
            else:   
                
                f = open(pathFile+str(route)+".gpx", 'r')
                p = gpxpy.parse(f)
                p.simplify()
                p.reduce_points(500)
                        
                points = p.tracks[0].segments[0].points
                for point in points:        
                    pA = (point.longitude,point.latitude)
                    for idx,pB in enumerate(coords):
                        dis = vincenty(pA, pB[0:2].tolist()).meters
                        if  dis<=tolerance:
                            sort_coords.append([pB[0],pB[1],route])   
                            coords = np.delete(coords,idx,0)
                            break
                    if len(coords)==0:
                        break
#                if len(coords)>0:
#                    print "\tHan quedado - puntos entre si cercanos: %i" %len(coords)
            sort_coords.append(routeCoordsSN[-1][0:3].tolist())  

            sort_routes.append(sort_coords)
            print "-"*50
            
    #==============================================================================
    # Rutas from bloques derechos de IN - can be improved...
    #==============================================================================
    routesB = np.unique(coordsIN[:,3]).astype(int)
    toleranceB = 100.0
    for route in routesB:
        if route in routes:
            continue
        
        routeCoordsSN = coordsSN[coordsSN[:,2]==route]
        routeCoordsIn = coordsIN[coordsIN[:,3]==route]
            
#        assert len(routeCoordsSN)<2
    
        sort_coords = []
        sort_coords.append(routeCoordsSN[0][0:3].tolist())   
        
        coords = np.concatenate((routeCoordsSN[1:-1],routeCoordsIn[:,0:3]))
            
        if len(coords) == 1:
            sort_coords.append(coords[0][0:3])
        else:   
            with open(pathFile+str(route)+".gpx", 'r') as f:              
                p = gpxpy.parse(f)
                p.simplify()
                p.reduce_points(500)
                        
                points = p.tracks[0].segments[0].points
                
                for point in points:        
                    pA = (point.longitude,point.latitude)  
                    for idx,pB in enumerate(coords):
                        dis = vincenty(pA, pB[0:2].tolist()).meters
                        if  dis<=toleranceB:
                            sort_coords.append([pB[0],pB[1],route])   
                            coords = np.delete(coords,idx,0)
                            break
                        if len(coords)==0:
                            break
#                if len(coords)>0:
#                    print "Han quedado - puntos entre si cercanos: IN"
                    
        sort_coords.append(routeCoordsSN[-1][0:3].tolist())                    

        sort_routes.append(sort_coords)
    
    routes = np.unique(coordsIN[:,2:4]).astype(int)
    
    result = []
    for sortR in sort_routes:
        for point in sortR:
            result.append(point)  
    
    result = np.array(result)
    
    with job.fileStore.writeGlobalFileStream() as (fileHandle, outComputeSNID):
        np.save(fileHandle,result)        

    job.fileStore.exportFile(outComputeSNID, 'file:///Users/isaac/IdeaProjects/Network_Workflow/FNodes.npy')
    
  
  
#      
#def helloWorld3(job, options):
#    job.fileStore.logToMaster("Hello 3")
#    sortFileID = job.fileStore.importFile('file:///Users/isaac/IdeaProjects/Network_Workflow/SNnodes.csv')
#    with job.fileStore.readGlobalFileStream(sortFileID) as fH:
#        codes2 = np.load(fH)
#
#    for code in codes2:
#        job.fileStore.logToMaster("HW3: code file: %s"%code)
#
#    time.sleep(2)
#    job.fileStore.logToMaster("END Hello 3")
