# Network Complex From Trajectories

This generates the complex network from a set of GPX trajectories. 
It is the implementation of this process:
"Analysing human mobility patterns of hiking activities through complex network theory" http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177712

It is implemented using TOIL workflow library. It requieres some improvements in order to execute in the cloud. Input files should be modified.

The main parameters are two: a path with GPX files, and a array (npy format) with the names of files. This separation is used to facilitates the selection of routes.

The dataset is not included

**Note** This version only generates a SHAPE file, but the result can be modified in module_Net for example:
nx.write_gexf(G,"test.gexf") 
nx.write_graphml(G,"test.graphml") 

Dependencies
------------
* [Toil](https://github.com/BD2KGenomics/toil)
* [gpxpy](https://github.com/tkrajina/gpxpy)
* [geopy](https://github.com/geopy/geopy)
* [networkx](https://github.com/networkx)
* numpy
* scipy 

Running
------------
python generateNetwork.py file:workflowname --pathGPX /path/to/dataset/GPXs/ --pathNPY /path/to/file/nameOfRoutes.npy

Some examples:
![Image of Example1](https://github.com/wisaaco/NetworkComplexFromTrajectories/blob/master/img/file1.png)
![Image of Example2](https://github.com/wisaaco/NetworkComplexFromTrajectories/blob/master/img/file2.png)
![Image of Example3](https://github.com/wisaaco/NetworkComplexFromTrajectories/blob/master/img/file3.png)
![Image of Example4](https://github.com/wisaaco/NetworkComplexFromTrajectories/blob/master/img/file4.png)


