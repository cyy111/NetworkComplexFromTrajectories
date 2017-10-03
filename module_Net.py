# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:31:15 2017

@author: isaac
"""


import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
import networkx as nx      
   
    
    
"""
Return Labels Of Cluster, Cluster Center 
LabelsOfCluster - array 1d int
Cluster Center -- arrat 2d lat,long
"""
def doCluster(coords):
    bandwidth = estimate_bandwidth(coords[:,:2], quantile=0.005) #0.01
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(coords[:,:2])
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_
    return labels,cluster_centers


#==============================================================================
# #NODOS
# select by THRESHOLD
#==============================================================================
      
"""
Return Nodes by Frequency of Groups
Params: Threshold 
"""    
def getNodes(coords,labels,treshold):
    nodosByLabel = {}
    for idx,et in enumerate(labels):
        if et in nodosByLabel.keys():
            if not coords[idx][2] in nodosByLabel[et]:
                nodosByLabel[et].append(coords[idx][2])
        else:
            nodosByLabel[et] = [coords[idx][2]]
    return nodosByLabel
    

#==============================================================================
# Uniones entre grupos
#==============================================================================
#La unión entre los grupos viene dada por la secuencia de codeRoute en coords
# OOPT: Filtrado aquellos grupos que no estarán en el TOP - nodosByLabel
"""
 Return sequence of arrays 1d[1d.size diff]
 
"""
def getEdges(coords,labels):
    previousRoute = 0
    seq = []
    seqRoute = []
    for idx,ruta in enumerate(coords[:,2]):
        if ruta != previousRoute: #comenzamos una nueva ruta
            previousRoute = ruta
            if len(seqRoute)>1 :
                seq.append(seqRoute)

            labelGroup = labels[idx]
            if labelGroup in nodosByLabel.keys():
                seqRoute = [labelGroup]
            else:
                seqRoute =[] #LINEA VITAL
        else:
            labelGroup = labels[idx]
            if labelGroup in nodosByLabel.keys():
                seqRoute.append(labelGroup)
                
    if len(seqRoute)>1 :
        seq.append(seqRoute)

    return seq
    

    
    
#==============================================================================
# RED
#==============================================================================
    
def createGraph(nodosByLabel,cluster_centers,seq):   
    G=nx.DiGraph()
#    G=nx.MultiGraph()
    for key in nodosByLabel.keys():
        lat=float(cluster_centers[key][0])
        lng=float(cluster_centers[key][1])
        n = G.add_node(key,
                       idN=float(key),
                       weight=float(len(nodosByLabel[key])),
                       lat = lat,
                       lng = lng
                       )
                     
    #Convertir la sequencia de route sobre en tupla edge o introducirla
    for path in seq:
        for i in range(0,len(path)-1):
            if path[i]!=path[i+1]:
                G.add_edge(path[i],path[i+1])
   
    return G

     
#==============================================================================
#==============================================================================
#==============================================================================
# # # MAIN
#==============================================================================
#==============================================================================
#==============================================================================

def runNetwork(job,options):
    coords = np.load("FNodes.npy")    

    labels, cluster_centers = doCluster(coords)   
    nodosByLabel = getNodes(coords,labels,4)

    ###Saving info nodes for QGIS app
    with job.fileStore.writeGlobalFileStream() as (fileHandle, outID):
        fileHandle.write("lat,long,frec\n")
        for idx,key in enumerate(nodosByLabel.keys()):
            fileHandle.write("%s,%s,%s,%i\n" % (idx,cluster_centers[key][0],cluster_centers[key][1],len(nodosByLabel[key])))
    
    job.fileStore.exportFile(outID, 'file:///Users/isaac/IdeaProjects/Network_Workflow/qgis_stats_nodes.csv')

    seq = getEdges(coords,labels)
    G = createGraph(nodosByLabel,cluster_centers,seq)
    
    #==============================================================================
    # Save: shaping file
    #==============================================================================
#    BUG of NX library 
    mapping = {}
    counter = 0
    for idx,d in enumerate(G.nodes):
        co_od=(G.node[d]["lat"],G.node[d]["lng"])
        mapping[counter] = co_od
        counter += 1
    G=nx.relabel_nodes(G, mapping)

    with job.fileStore.writeGlobalFileStream() as (fileHandle, outID):
        nx.write_shp(G,fileHandle)    

    job.fileStore.exportFile(outID, 'file:///Users/isaac/IdeaProjects/Network_Workflow/shape')
    
