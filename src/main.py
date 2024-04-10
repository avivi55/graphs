from time import sleep

from tabulate import tabulate
from Graph import Graph
from rich import print, table

graphs = [Graph(i) for i in range(1, 15)]


i = 0

# while (True):
#     i += 1
#     i = i % 14
#     print(graphs[i])
#     print(tabulate(graphs[i].get_value_matrix(), tablefmt="rounded_grid"))
    
#     # print(graphs[i].has_negative_arcs())
#     # print(graphs[i].has_circuit_by_transitive())
#     if not graphs[i].has_circuit_by_transitive():
#         print(graphs[i].get_ranks())  
#         print(graphs[i].get_early_calendar())  
#         print(graphs[i].get_late_calendar())  
    
#     sleep(0.5)


# print(Graph(path_override="./graphs/test_2.txt").get_ranks())
print(Graph(path_override="./graphs/test_2.txt").table)
print(Graph(path_override="./graphs/test_2.txt").get_early_calendar())
print(Graph(path_override="./graphs/test_2.txt").get_late_calendar())
print(Graph(path_override="./graphs/test_2.txt").get_margins())