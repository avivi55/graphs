import os
from pathlib import Path

from tabulate import tabulate
from F3_Graph import Graph
from rich import print, table
import graphviz

graphs = [Graph.from_file(i) for i in range(1, 15)]

DIR = Path(__file__).parent.parent

for graph in graphs:
    with open((DIR / Path(f"traces/F3_{graph.number}.txt")), mode="w") as f:
        graphviz.Source(graph.to_dot_format()) \
            .render(outfile=((DIR / Path(f"traces/F3_{graph.number}.png"))), view=False, format="png")
        
        os.remove(Path(DIR) / Path(f'traces/F3_{graph.number}.gv'))
        
        f.write(f"Graphe de test n°{graph.number}")
        f.write('\n')
        
        f.write('\n')
        t = table.Table(title="Table des contraintes", show_lines=True)
        
        t.add_column("noeud")
        t.add_column("durée")
        t.add_column("prédécesseurs")
        
        constraints = graph.get_constraint_table()
        
        for node in graph.table.keys():
            t.add_row(str(node), str(list(constraints[node].keys())[0]), ','.join([str(x) for x in list(constraints[node].values())[0]]))
        
        print(t, file=f)
        
        
        
        f.write('\n')
        f.write("Matrice\n")
        print(graph, file=f)
        
        f.write('\n')
        f.write("Matrice des valeurs\n")
        print(tabulate(graph.get_value_matrix(), tablefmt="rounded_grid"), file=f)
        
        f.write('\n')
        f.write("Aucunes valeurs n'est négative\n")
        
        has_circuit, steps = graph.has_circuit_by_deletions(True)
        
        f.write('\n')        
        f.write("Calcul de circuit.\n")
        for step in steps:
            print(f"suppression de {step}", file=f)
        
        if has_circuit:
            f.write("Nous n'avons pas pu supprimer tout les noeuds du graphe : Le graphe a au moins un circuit\n")
        else:
            f.write("Tout les noeuds ont pu être supprimés : Le graphe n'a pas de circuit\n")
            f.write("C'est un graphe d'ordonnancement\n")
            
            
            ranks = graph.ranks
            
            latest = dict(sorted(graph.get_latest_calendar().items(), key=lambda x: ranks.get(x[0])))
            earliest = dict(sorted(graph.get_earliest_calendar().items(), key=lambda x: ranks.get(x[0])))
            margins = dict(sorted(graph.get_margins().items(), key=lambda x: ranks.get(x[0])))
            
            
            f.write('\n')  
            t = table.Table(title="Rangs", show_lines=True)
            
            t.add_column("noeud")
            for e in graph.table.keys():
                t.add_column(str(e))
            
            t.add_row("rang", *[str(ranks.get(x)) for x in graph.table.keys()])
    
            print(t, file=f)
            
            
            f.write('\n')
            
            t = table.Table(title="Calendrier au plus tôt", show_lines=True)
            
            t.add_column("rang")

            for e in ranks.values():
                t.add_column(str(e))
                
            t.add_row("noeud", *[f"{k}({graph.get_node_time(k)})" for k in ranks.keys()])
            t.add_row("prédécesseurs", *[','.join([str(x) for x in graph.get_predecessors(n)]) for n in ranks.keys()])
            
            t.add_row("dates au plus tôt", *[str(x) for x in earliest.values()])
            
            print(t, file=f)



            f.write('\n')
            
            t = table.Table(title="Calendrier au plus tard", show_lines=True)
            
            t.add_column("rang")

            for e in ranks.values():
                t.add_column(str(e))
                
            t.add_row("noeud", *[f"{k}({graph.get_node_time(k)})" for k in ranks.keys()])
            t.add_row("successeurs", *[','.join([str(x) for x in graph.get_successors(n)]) for n in ranks.keys()])
            
            t.add_row("dates au plus tard", *[str(x) for x in latest.values()])
            
            print(t, file=f)
            
            
            
            f.write('\n')
            
            t = table.Table(title="Marges", show_lines=True)
            
            t.add_column("rang")
            for e in ranks.values():
                t.add_column(str(e))
                
            t.add_row("noeud", *[f"{k}" for k in ranks.keys()])
            
            t.add_row("dates au plus tard", *[str(x) for x in latest.values()])
            t.add_row("dates au plus tôt", *[str(x) for x in earliest.values()])
            t.add_row("marges", *[str(x) for x in margins.values()])
            
            print(t, file=f)


            f.write('\n')
            f.write("Plus long chemins\n")
            print(graph.get_longest_path(), file=f)
            
            graphviz.Source(graph.to_dot_format(True)) \
                .render(outfile=((DIR / Path(f"traces/F3_{graph.number}_highlighted_path.png"))), view=False, format="png")
                
            os.remove(Path(DIR) / Path(f'traces/F3_{graph.number}_highlighted_path.gv'))
        
            
        
        