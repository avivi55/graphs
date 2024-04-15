from pathlib import Path

from tabulate import tabulate
from Graph import Graph
from rich import print, table
import graphviz


graphs: list[Graph] = [Graph.from_file(i) for i in range(1, 15)]

main_prompt_message = "Entrez le numéro d'un graphe [1; 14]\n"

graph_prompt_message = {
    "a": "Retourner au menu principal",
    "z": "Afficher la matrice de valeurs",
    "e": "Informations sur le graphe",
    "r": "Calendriers",
    "t": "Afficher le graphe (graphique)",
    "y": "Afficher le.s chemin.s critique.s",
    "u": "Afficher le.s chemin.s critique.s (graphique)"
}


def get_infos(x: int):
    print()
    
    if graphs[x].negative_arcs:
        print("Le graphe à des arcs à valeurs négatives")
    else:
        print("Aucunes valeurs d'arc n'est négative")
    
    if graphs[x].has_circuit:
        print("Le graphe a au moins un circuit")
    else:
        print("Le graphe n'a pas de circuit")
        
        
    if graphs[x].negative_arcs and not graphs[x].has_circuit: 
        print("Toutes les conditions sont vérifiée, c'est un graphe d'ordonnancement")
    
    print()
        
def get_calendars(x:int):
    if graphs[x].has_circuit or graphs[x].negative_arcs:
        print("\nle graphe n'est pas un graphe d'ordonnancement\n")
        return
    ranks = graphs[x].get_ranks()
            
    latest = dict(sorted(graphs[x].get_latest_calendar().items(), key=lambda x: ranks.get(x[0])))
    earliest = dict(sorted(graphs[x].get_earliest_calendar().items(), key=lambda x: ranks.get(x[0])))
    margins = dict(sorted(graphs[x].get_margins().items(), key=lambda x: ranks.get(x[0])))
    
    t = table.Table(title="Rangs", show_lines=True)
    t.add_column("noeud")
    for e in graphs[x].table.keys():
        t.add_column(str(e))
    t.add_row("rang", *[str(ranks.get(x)) for x in graphs[x].table.keys()])
    print(t)
    
    t = table.Table(title="Calendrier au plus tôt", show_lines=True)
    t.add_column("rang")
    for e in ranks.values():
        t.add_column(str(e)) 
    t.add_row("noeud", *[f"{k}({graphs[x].get_node_time(k)})" for k in ranks.keys()])
    t.add_row("prédécesseurs", *[','.join([str(x) for x in graphs[x].get_predecessors(n)]) for n in ranks.keys()])
    t.add_row("dates au plus tôt", *[str(x) for x in earliest.values()])
    print(t)

    
    t = table.Table(title="Calendrier au plus tard", show_lines=True)
    t.add_column("rang")
    for e in ranks.values():
        t.add_column(str(e))
    t.add_row("noeud", *[f"{k}({graphs[x].get_node_time(k)})" for k in ranks.keys()])
    t.add_row("successeurs", *[','.join([str(x) for x in graphs[x].get_successors(n)]) for n in ranks.keys()])
    t.add_row("dates au plus tard", *[str(x) for x in latest.values()])
    print(t)
    
    t = table.Table(title="Marges", show_lines=True)
    t.add_column("rang")
    for e in ranks.values():
        t.add_column(str(e))
    t.add_row("noeud", *[f"{k}" for k in ranks.keys()])
    t.add_row("dates au plus tard", *[str(x) for x in latest.values()])
    t.add_row("dates au plus tôt", *[str(x) for x in earliest.values()])
    t.add_row("marges", *[str(x) for x in margins.values()])
    print(t)


DIR = Path(__file__).parent.parent

def show_graph(x: int, path: bool):
    if graphs[x].has_circuit or graphs[x].negative_arcs or not path:
        graphviz.Source(graphs[x].to_dot_format()) \
            .render(outfile=((DIR / Path(f"traces/{graphs[x].number}.png"))), view=True, format="png")
        return
    
    graphviz.Source(graphs[x].to_dot_format(True)) \
        .render(outfile=((DIR / Path(f"traces/{graphs[x].number}_highlighted_path.png"))), view=True, format="png")
        
    
graph_commands = {
    "z": lambda x: print(tabulate([[f"{i}"] + g for (i, g) in enumerate(graphs[x].get_value_matrix())], tablefmt="rounded_grid", headers=[f"n°{graphs[x].number}"]+[str(i) for i in range(graphs[x].size)])),
    "e": lambda x: get_infos(x),
    "r": lambda x: get_calendars(x),
    "t": lambda x: show_graph(x, False),
    "y": lambda x: print("\nle graphe n'est pas un graphe d'ordonnancement\n" if (graphs[x].has_circuit or graphs[x].negative_arcs) else graphs[x].get_longest_path()),
    "u": lambda x: show_graph(x, True),
}

def focus_on_graph(number: int):
    while(True):
        for k, v in graph_prompt_message.items():
            print(f"{k}. {v}")
        user_command = input("Choisissez une option : ")
        
        if user_command == 'a':
            return
        
        if not user_command in graph_commands.keys():
            continue
        
        graph_commands[user_command](number)


while(True):
    print(main_prompt_message)
    
    try:
        user_command = input("Choisissez : ")
        graph = int(user_command) - 1
        
        if 0 <= graph < len(graphs):
            focus_on_graph(graph)
            print()
        
    except ValueError:
        continue
    
    except KeyboardInterrupt:
        print()
        break