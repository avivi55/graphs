from pathlib import Path
from Graph import Graph
from rich import print, table
import graphviz

graphs = [Graph.from_file(i) for i in range(1, 15)]


for graph in graphs:
    with open((Path(__file__).parent.parent / Path(f"traces/{graph.number}.txt")), mode="w") as f:
        f.write("Table des contraintes\n")
        print(graph.get_constraint_table(), file=f)
        f.write("\nMatrice\n")
        print(graph, file=f)
        
        if graph.has_circuit_by_deletions()[0]:
            f.write("\nLe graphe a au moins un circuit")
        else:
            f.write("\nLe graphe n'a pas de circuit")
            
            f.write("\nRangs\n")
            print(graph.get_ranks(), file=f)
            f.write("\nMarges\n")
            print(graph.get_margins(), file=f)
            f.write("\nPlus long chemins\n")
            print(graph.get_longest_path(), file=f)
            
        
        