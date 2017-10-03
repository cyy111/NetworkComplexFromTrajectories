# Network Complex From Trajectories

This generates the complex network from a set of GPX trajectories. 
It is the implementation of this process: http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177712

It is implemented using TOIL workflow library. It requieres some improvements in order to execute in the cloud. Input files should be modified.

The main parameters are two: a path with GPX files, and a array (npy format) with the names of files. This separation is used to facilitates the selection of routes.

The dataset is not included

**Note** This version only generates a SHAPE file, but the result can be modified in module_Net for example:
nx.write_gexf(G,"test.gexf") 
nx.write_graphml(G,"test.graphml") 

Dependencies
------------
* `toil <https://github.com/BD2KGenomics/toil>`__
* `gpxpy <https://github.com/tkrajina/gpxpy>`__
* `geopy <https://github.com/geopy/geopy>`__
* `networkx <https://github.com/networkx>`__
* numpy
* scipy 


Some examples:

[[https://github.com/wisaaco/NetworkComplexFromTrajectories/img/file1.png|alt=octocat]]

