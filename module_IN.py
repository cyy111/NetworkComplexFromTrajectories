# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:13:49 2017

@author: isaac
"""

import scipy.spatial
import gpxpy
import numpy as np
import pandas as pd

def getRegions(seq):
    regions = []
    previousReg = False
    for i in range(1,len(seq)-1):
        if seq[i]>0 and not previousReg:
            regions.append(i)
            previousReg = True
        elif seq[i]<=0 and previousReg:
            #en estado de un posible fin
            check = True
            if (i<len(seq)-2):
                if seq[i+1]<=0 and seq[i+2]<=0:
                    check = False
            if not check:
                regions.append(i-1)
                previousReg = False
    return regions





def computeIN(job,options):

#==============================================================================
#   IMPORT FILES SHOULD BE IMPROVED
#==============================================================================
    pathDst = options.pathGPX
    rutas = np.load(options.pathNPY)

    job.fileStore.logToMaster("START IN")
    tolerance = 0.0005
    match = np.array([])
    for code in rutas:
#        logging.info("+ Main Route %s" %code)
        points_a = []
        try:
            pathFile1 = pathDst+str(code)+".gpx"
            job.fileStore.logToMaster("IN: Route: %s"%pathFile1)
            with open(pathFile1, 'r') as f:
                p = gpxpy.parse(f)
                p.simplify()
                p.reduce_points(500)
                for track in p.tracks:  # OJO SOLO HAY UN TRACK
                    for segment in track.segments:  # OJO SOLO HAY UN SEGMENT
                        for iA in range(0,len(segment.points)-1):
                            point = segment.points[iA]
                            points_a.append([point.longitude,point.latitude])
    
            points_a = np.vstack(points_a)
    
            for code2 in rutas:
                if code == code2:
                    continue
#                print "\t code: %s" %code2
                try:
                    pathFile2  = pathDst+str(code2)+".gpx"
                    points_b = []
                    with open(pathFile2, 'r') as f:
                        p = gpxpy.parse(f)
                        p.simplify()
                        p.reduce_points(500)
                        for track in p.tracks:  # OJO SOLO HAY UN TRACK
                            for segment in track.segments:  # OJO SOLO HAY UN SEGMENT
                                for iA in range(0,len(segment.points)-1):
                                    point = segment.points[iA]
                                    points_b.append([point.longitude,point.latitude])
        
        
                    points_b = np.vstack(points_b)
                    all_trails = [points_a, points_b]
                    labelled_pts = np.vstack([np.hstack([a, np.ones((a.shape[0], 1)) * i])
                                              for i, a in enumerate(all_trails)
                                              ])
        
                    tree = scipy.spatial.KDTree(labelled_pts[:, :2])
                    points_within_tolerance = tree.query_ball_point(labelled_pts[:, :2], tolerance)
        
                    vfunc = np.vectorize(lambda a: np.any(labelled_pts[a, 2] != labelled_pts[a[0], 2]))
        
                    matches = vfunc(points_within_tolerance)
#                    logging.info("\t+ Computed matches " )
                    x = np.vstack([labelled_pts[:,0] ,labelled_pts[:,1],labelled_pts[:,2],matches])
                    x = x.T
                    df = pd.DataFrame(x)
        
                    ruta1 = df[df[2]==0]
        
                    seq = ruta1[3]
        
                    regions1 = getRegions(seq)

                    if len(match)==0:
                        aco = np.vstack(np.full((len(labelled_pts[regions1][:,:2]),),code ))
                        acd = np.vstack(np.full((len(labelled_pts[regions1][:,:2]),),code2))
                        match = np.hstack((labelled_pts[regions1][:,:2],aco,acd)) 
                    elif len(labelled_pts[regions1][:,:2])>0:
                        
                        aco = np.vstack(np.full((len(labelled_pts[regions1][:,:2]),),code ))
                        acd = np.vstack(np.full((len(labelled_pts[regions1][:,:2]),),code2))
                        match = np.concatenate((match,np.hstack((labelled_pts[regions1][:,:2],aco,acd)) ))
                        
#                    print "\t done" 
                except:
#                    print "\t Imposible procesar ruta: %s"%code2
                    None
    
        except:
            None
#            print "\n errorrrrr "
    
        #end for2
    #end for1
    with job.fileStore.writeGlobalFileStream() as (fileHandle, outID):
        np.savetxt(fileHandle,match,delimiter=",",fmt='%s,%s,%s,%s')        

    job.fileStore.exportFile(outID, 'file:///Users/isaac/IdeaProjects/Network_Workflow/INnodes.csv')

