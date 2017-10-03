# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 08:56:12 2017

@author: isaac
"""
from argparse import ArgumentParser
import os
import numpy as np
from toil.common import Toil
from toil.job import Job


from module_SN import computeSN
from module_IN import computeIN
from module_F import joinSNIN
from module_Net import runNetwork

#python generateNetwork.py file:jobStore --pathGPX /Users/isaac/IdeaProjects/QGISphase/src/cimas/cimasData/Massanella/ --pathNPY /Users/isaac/IdeaProjects/QGISphase/src/cimas/cimasData/rutas_on_Massanella_Summer.npy
 

# 
     #rutas = np.load("cimasData/rutas_on_Teide_Spring.npy")
    #rutas = np.load("cimasData/rutas_on_Teide_Winter.npy")
    #rutas = np.load("cimasData/rutas_on_Massanella_Spring.npy")
#    rutas = np.load("cimasData/rutas_on_Massanella_Summer.npy")

#==============================================================================
# DAG of jobs 
#==============================================================================
def generateNetwork(job,options):
#    outComputeSN = None
    j1 = Job.wrapJobFn(computeSN,options)
    j2 = Job.wrapJobFn(computeIN,options)
    j3 = Job.wrapJobFn(joinSNIN,options)
    j4 = Job.wrapJobFn(runNetwork, options)
    
    job.addChild(j1)
    job.addChild(j2)
    job.addFollowOn(j3)
    j3.addFollowOn(j4)
    

#defaultOutPath = "tmp"

def main(options=None):
    if not options:
        parser = ArgumentParser()
        Job.Runner.addToilOptions(parser)
        parser.add_argument('--pathGPX',help='The absolute path where all GPX file are.')
        parser.add_argument('--pathNPY', help='A npy file (np.array stored) with the path of each file to be analysed')
#        parser.add_argument("--O",  help="Output destination path ",default=defaultOutPath)

        options = parser.parse_args()
    
    #some checks
    npyFile = options.pathNPY 
    if not os.path.exists(npyFile):
        print("the npy file [fileNameGPX1,fileNameGPX2,...] does not exists.")
        exit()

    try:
        codes = np.load(npyFile)
        if len(codes)==0:
            raise RuntimeError("Invalid values of npy file: %s" % options.pathNPY)
    except:
        raise RuntimeError("Invalid format of npy file: %s" % options.pathNPY)

    #Run workflow    
    with Toil(options) as workflow:
        if not workflow.options.restart:
            workflow.start(Job.wrapJobFn(generateNetwork,options=options))
        else:
            workflow.restart()
#        workflow.exportFile(sortedFileID, sortedFileURL)
        
        
if __name__ == '__main__':
    main()


