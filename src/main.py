from time import sleep

from tabulate import tabulate
from Graph import Graph
from rich import print, table
import graphviz

graphs = [Graph(i) for i in range(1, 15)]


i = 0

while (True):
    # print(graphs[i])
    # print(tabulate(graphs[i].get_value_matrix(), tablefmt="rounded_grid"))
    
    # print(graphs[i].has_negative_arcs())
    # print(graphs[i].has_circuit_by_transitive())
    if not graphs[i].has_circuit_by_transitive():
        graphviz.Source(graphs[i].to_dot_format(True)) \
            .render(outfile=(f'out/{i+1}.png'), view=False, format="png")
    else:
        graphviz.Source(graphs[i].to_dot_format()) \
            .render(outfile=(f'out/{i+1}.png'), view=False, format="png")
    
    i += 1
    if i == 14: break
    # sleep(0.5)


# print(Graph(path_override="./graphs/test_2.txt").get_ranks())
# print(Graph(path_override="./graphs/test_1.txt").table)
# print(Graph(path_override="./graphs/test_2.txt").get_early_calendar())
# print(Graph(path_override="./graphs/test_2.txt").get_late_calendar())
# print(Graph(path_override="./graphs/test_2.txt").get_margins())
# print(Graph(path_override="./graphs/test_2.txt").get_critical_path())
# if not Graph(path="./graphs/test_1.txt").has_circuit_by_transitive():
#     print(Graph(path="./graphs/test_2.txt").get_critical_nodes())

