from time import sleep

from tabulate import tabulate
from Graph import Graph
from rich import print, table
import graphviz

graphs = [Graph.from_file(i) for i in range(1, 15)]


# i = 0

# while (True):
    # print(graphs[i])
    # print(tabulate(graphs[i].get_value_matrix(), tablefmt="rounded_grid"))
    
    # print(graphs[i].has_negative_arcs())
    # print(graphs[i].has_circuit_by_transitive())
    # if not graphs[i].has_circuit_by_transitive():
    #     graphviz.Source(graphs[i].to_dot_format(True)) \
    #         .render(outfile=(f'out/{i+1}.png'), view=False, format="png")
    #     print(graphs[i].get_critical_path())
    # else:
    #     graphviz.Source(graphs[i].to_dot_format()) \
    #         .render(outfile=(f'out/{i+1}.png'), view=False, format="png")
    
    # i += 1
    # if i == 14: break
    # sleep(0.5)

graphviz.Source(Graph.from_file(path="./graphs/6.txt").to_dot_format(highlight_critical_path=True)) \
            .render(outfile=(f'out/test.png'), view=False, format="png")
# print(Graph.from_file(path="./graphs/6.txt").get_sub_graph(2).get_longest_path())
# print(Graph.from_file(path="./graphs/6.txt").get_sub_graph(3).get_longest_path())
print(Graph.from_file(path="./graphs/6.txt").get_sub_graph(4).get_critical_path())
print(Graph.from_file(path="./graphs/6.txt").get_sub_graph(4).get_longest_path())
# print(Graph.from_file(path="./graphs/6.txt").get_sub_graph(4).get_critical_nodes())
# print(Graph.from_file(path="./graphs/13.txt").get_ranks())
# print(Graph.from_file(path="./graphs/13.txt").get_critical_path())
# print(Graph(path_override="./graphs/test_1.txt").table)
# print(Graph(path_override="./graphs/test_2.txt").get_early_calendar())
# print(Graph(path_override="./graphs/test_2.txt").get_late_calendar())
# print(Graph(path_override="./graphs/test_2.txt").get_margins())
# print(Graph(path_override="./graphs/test_2.txt").get_critical_path())
# if not Graph(path="./graphs/test_1.txt").has_circuit_by_transitive():
#     print(Graph(path="./graphs/test_2.txt").get_critical_nodes())

