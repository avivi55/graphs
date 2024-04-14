from time import sleep

from tabulate import tabulate
from Graph import Graph
from rich import print, table
import graphviz

graphs = [Graph.from_file(i) for i in range(1, 15)]



# print(graphs[0].get_matrix())
# print(graphs[0].table)

for graph in graphs:

    if not graph.has_circuit_by_deletions()[0]:
        graphviz.Source(graph.to_dot_format(True)) \
            .render(outfile=(f'out/{graph.number}.png'), view=False, format="png")
    else:
        graphviz.Source(graph.to_dot_format()) \
            .render(outfile=(f'out/{graph.number}.png'), view=False, format="png")

