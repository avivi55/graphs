from pathlib import Path
from pprint import pprint
from matplotlib.pyplot import margins
from networkx import predecessor
from tabulate import tabulate
from rich import table
class Graph:
    """
        The graph is represented using a dictionary with this form:
        
        {
            'node_n': {
                'node_k': time,
                'node_k2': time,
                'node_k3': time
            },
            'node_n+1': {
                'node_k': time,
            }, 
            ...
        }
    """ 
    
    def __init__(self, number: int = 0, path_override: str = "") -> None:
        
        if (path_override == ""):
            with (Path(__file__).parent.parent / Path(f"graphs/{number}.txt")).open() as f:
                self.data: str = f.read()
            self.number = number
        else:
            with Path(path_override).open() as f:
                self.data: str = f.read()
            self.number = 'X'
            
        
        _filter = lambda s: list(filter(lambda x: x, s))
        splitted_data: list[str] = _filter(self.data.split('\n'))
        
        splitted_string: list[list[str]] = [_filter(string.split(' ')) for string in splitted_data]
        
        self.table: dict[str, dict[str, int]] = self._table_from_valid_list(splitted_string)          
    
        
    def _table_from_valid_list(self, splitted_string: list[list[str]]) -> dict[str, dict[str, int]]:

        table: dict[str, dict[str, int]] = {}
                
        nodes: list[str] = [s[0] for s in splitted_string]
        
        # initialization of the table
        for node in nodes:
            if node not in table.keys():
                table[node] = {}
        
        table['0'] = {}
        
        size: int = len(table.keys())
        
        table[str(size)] = {}
       
        size += 1
        # We just added 2 to the size because of the the 2 new implicit states: alpha & omega
        all_predecessors: list[str] = self._get_all_predecessors(splitted_string)
        
        for line in splitted_string:
            
            label: str = line[0]
            predecessors: list[str] = line[2:]
            
            if not predecessors:
                table['0'] |= {label: 0}
                continue
            
            if label not in all_predecessors:
                # we subtract 2 because we added ɑ & ω
                old_size: int = size-2
                table[str(label)] = {str(size-1): int(splitted_string[old_size-1][1])}
            
            for node in predecessors:
                table[node] |= {label: int(splitted_string[int(node)-1][1])}
        
        self.size: int = len(table.keys())
        return table
    
    def _get_all_predecessors(self, splitted_string) -> list[str]:
        predecessors: list[str] = []
        
        for line in splitted_string:
            predecessors += line[2:]
            
        return list(set(predecessors))
    
    def has_negative_arcs(self) -> bool:
        for line in self.table.values():
            for value in line.values():
                if value < 0:
                    return True 
        return False
    
    def get_matrix(self) -> list[list[int]]:
        length = len(self.table.keys())
        matrix = [[] for _ in range(length)]
        
        for k, v in self.table.items():
            matrix[int(k)] = [1 if str(i) in v.keys() else 0 for i in range(length)]
            
        return matrix
    
    
    def get_value_matrix(self):
        length = len(self.table.keys())
        matrix = [[] for _ in range(length)]
        
        for k, v in self.table.items():
            matrix[int(k)] = [v.get(str(i)) if str(i) in v.keys() else 0 for i in range(length)]
            
        return matrix
    
    def _get_predecessors(self, node):
        
        if node not in self.table.keys():
            return []
        
        predecessors = []
        for label, successors in self.table.items():
            if node in successors.keys():
                predecessors.append(label)
                
        return list(set(predecessors))
                
        
    def get_constraint_table(self):
        table = {}
        
        for label, successors in self.table.items():
            if time:=list(successors.values()):
                table[label] = {time[0]: self._get_predecessors(label)}
            else:
                table[label] = {0: self._get_predecessors(label)}
                
        return table
    
    def has_circuit_by_transitive(self) -> bool:
        transitive = self.get_matrix()
        n = len(transitive)
        
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    transitive[i][j] = transitive[i][j] or (transitive[i][k] and transitive[k][j])
                    
        return 1 in [transitive[i][i] for i in range(n)]
    
    def has_circuit_by_deletions(self, step:bool = False):
        
        steps = []
        
        #stupid hack for backwards compatibility, I AM FUCKING STUPID
        constraint: list[list[str | list[str]]] = [[k] + [str(e) for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        
        deleted_nodes: list[str] = []
                
        for _ in range(len(constraint)):
            is_impossible = 0
            
            for line in constraint:
                _line = line[:2] + [list(filter(lambda x: x not in deleted_nodes, line[2]))]

                if _line[2]:
                    is_impossible += 1
                    continue
                
                constraint.remove(line)
                deleted_nodes.append(line[0]) # type: ignore
                
                if step:
                    steps.append(constraint.copy()) # type: ignore
            
            if is_impossible == 0:
                return False, steps
            
        return True, steps
    
    def get_ranks(self):
        
        if self.has_circuit_by_transitive():
            raise ValueError("The graph has a circuit !!!! get fucked loser")
        
        constraint: list[list[str | list[str]]] = [[k] + [str(e) for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        deleted_nodes: list[str] = []
        ranks = {}
        
        current_rank = 0
        while (len(constraint) > 0):
                        
            for line in constraint:
                
                label: str = line[0] # type:ignore
                predecessors = line[2]
                if predecessors:
                    continue
                
                ranks[label] = current_rank
                deleted_nodes.append(label)
            
            constraint = list(filter(lambda l: l[0] not in deleted_nodes, constraint))
            constraint = [line[:2] + [list(filter(lambda x: x not in deleted_nodes, line[2]))] for line in constraint]
            
            current_rank +=1
            
        return ranks
    
    def _get_node_time(self, node):
        if not node in self.table.keys():
            raise ValueError("node not in graph")
        
        l = list(self.table[node].values())
        return l[0] if len(l) > 0 else 0
    
    def _get_successors(self, node):
        
        if node not in self.table.keys():
            return []
        
        return list(self.table[node].keys())
    
    def get_node_max_time(self, node):
        predecessors = self._get_predecessors(node)
        if not predecessors:
            return 0
        
        return max([self.get_node_max_time(x) + self._get_node_time(x) for x in predecessors])

    def get_node_min_time(self, node):
        successors = self._get_successors(node)
        if not successors:
            return self.get_node_max_time(node)
        
        return min([self.get_node_min_time(x) - self._get_node_time(node) for x in successors])
        
    def get_early_calendar(self):
        
        ranks = self.get_ranks()
               
        return [self.get_node_max_time(n)for n in ranks.keys()]
        
    def get_late_calendar(self):
        
        ranks = self.get_ranks()
        
        return [self.get_node_min_time(n) for n in ranks.keys()]
    
    
    def get_margins(self):
        
        ranks = self.get_ranks()
        
        early = [self.get_node_min_time(n) for n in ranks.keys()]
        late = [self.get_node_max_time(n) for n in ranks.keys()]

        return [a - b for a,b in zip(early, late)]
    
    

    # t = table.Table(title="Calendrier au plus tard", show_lines=True)
    
    # t.add_column("rank")
    
    # for e in ranks.values():
    #     t.add_column(str(e))
        
    # t.add_row("node", *[f"{k}({self._get_node_time(k)})" for k in ranks.keys()])
    # t.add_row("successors", *[','.join(self._get_successors(n)) for n in ranks.keys()])
    # t.add_row("calendar", *)
    
    def get_critical_path(self):
        
        rank = self.get_ranks()
        
        margins = self.get_margins()
        
        
        return []
        
        
        
        
        
    def __str__(self) -> str:
        
        matrix: list[list[str]] = [[f"{i}"] + ['.' for _ in range(self.size)] for i in range(self.size)]
        
        for node, trans in self.table.items():           
            for _node in trans.keys():
                matrix[int(node)][int(_node)+1] = '1'
                
        return tabulate(matrix, tablefmt="rounded_grid", headers=[f"n°{self.number}"]+[str(i) for i in range(self.size)])
    
