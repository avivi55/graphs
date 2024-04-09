from time import sleep
from Graph import Graph
from pathlib import Path 

graphs = [Graph(i) for i in range(1, 15)]


i = 0

while (True):
    i += 1
    i = i % 13
    print(graphs[i])
    
    print(graphs[i].has_negative_arcs())
    print(graphs[i].has_circuit_by_transitive())
    
    sleep(1)