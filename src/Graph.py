from pathlib import Path
from subprocess import list2cmdline
from typing import Any
from tabulate import tabulate
from rich import print, table

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
    def __init__(self, table: dict):
        
        self.table: dict = table.copy()
        self.number = 'X'
        self.ranks = {}
        self.size = len(table.keys()) 
        self.first_node = list(self.table.keys())[0]
        if not self.has_circuit_by_transitive():
            self.ranks = self.get_ranks() 
            
        
    @classmethod    
    def from_file(cls, number: int = 0, path: str = "", string_override= False):
        
        
        if (string_override):
            data = path # type: ignore
        elif (path == ""):
            with (Path(__file__).parent.parent / Path(f"graphs/{number}.txt")).open() as f:
                data: str = f.read()
            number = number
        else:
            with Path(path).open() as f:
                data: str = f.read()
            
        
        _filter = lambda s: list(filter(lambda x: x, s))
        splitted_data: list[str] = _filter(data.split('\n'))
        
        splitted_string: list[list[int]] = [[int(i) for i in _filter(string.split(' '))] for string in splitted_data]
        
        table: dict[int, dict[int, int]] = cls.table_from_valid_list(splitted_string)
        
        g = Graph(table)
        
        g.number = number
        
        return g
      
        
    def to_dot_format(self, highlight_critical_path=False):
        to_dot = "digraph { rankdir=LR\n"
        
        crit: list = []
        ranks: dict = {}
        path = {}
        if highlight_critical_path:
            ranks = self.ranks
            crit = self.get_critical_nodes()
            path = self.get_longest_path()
            for n in crit:
                to_dot += f'    "{n}" [color="red" label="{n}"]\n'
        
        for node, succs in self.table.items():
            for k, v in succs.items():
                to_dot += f'    "{node}" -> "{k}" [label="{v}"'
                
                if k in crit and node == 0:
                    to_dot += ' color="red"'
                
                if path.get(node) and k in path.get(node): # in crit and k in crit:
                    to_dot += ' color="red"'
                
                to_dot +=' ]\n'
                    
        to_dot += "}"
        return to_dot
    
    @classmethod
    def table_from_valid_list(cls, splitted_string: list[list[int]]):

        table: dict[int, dict[int, int]] = {}
                
        nodes: list[int] = [int(s[0]) for s in splitted_string]
        
        # initialization of the table
        for node in nodes:
            if node not in table.keys():
                table[node] = {}
        
        table[0] = {}
        
        size: int = len(table.keys())
        
        table[size] = {}
       
        size += 1
        # We just added 2 to the size because of the the 2 new implicit states: alpha & omega
        all_predecessors: list[int] = cls.__get_all_predecessors(splitted_string)
        
        for line in splitted_string:
            
            label: int = int(line[0])
            predecessors: list[int] = [int(i) for i in line[2:]]
            
            if not predecessors:
                table[0] |= {label: 0}
                continue
            
            if label not in all_predecessors:
                # we subtract 2 because we added ɑ & ω
                old_size: int = size-2
                table[label] = {size-1: int(splitted_string[label-1][1])}
            
            for node in predecessors:
                table[node] |= {label: int(splitted_string[int(node)-1][1])}
        
        # self.size: int = len(table.keys())
        return table
    
    @classmethod
    def __get_all_predecessors(cls, splitted_string) -> list[int]:
        predecessors: list[int] = []
        
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
        matrix = [[] for _ in range(self.size)]
        
        for i, (k, v) in enumerate(self.table.items()):
            matrix[i] = [1 if i in v.keys() else 0 for i in range(self.size)]
            
        return matrix  
    
    def get_value_matrix(self):
        length = len(self.table.keys())
        matrix = [[] for _ in range(length)]
        
        for k, v in self.table.items():
            matrix[int(k)] = [v.get(i) if i in v.keys() else '' for i in range(length)]
            
        return matrix
    
    def get_predecessors(self, node):
        
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
                table[label] = {time[0]: self.get_predecessors(label)}
            else:
                table[label] = {0: self.get_predecessors(label)}
                
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
        constraint: list[list[Any]] = [[k] + [e for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        
        deleted_nodes: list[int] = []
                
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
        
        # if self.has_circuit_by_transitive():
        #     raise ValueError("The graph has a circuit !!!! get fucked loser")
        
        constraint: list[list[Any]] = [[k] + [e for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        deleted_nodes: list[int] = []
        ranks = {}
        
        current_rank = 0
        while (len(constraint) > 0):
                        
            for line in constraint:
                
                label: int = line[0] # type:ignore
                predecessors = line[2]
                if predecessors:
                    continue
                
                ranks[label] = current_rank
                deleted_nodes.append(label)
            
            constraint = list(filter(lambda l: l[0] not in deleted_nodes, constraint))
            constraint = [line[:2] + [list(filter(lambda x: x not in deleted_nodes, line[2]))] for line in constraint]
            
            current_rank +=1
            
        return ranks
    
    def get_node_time(self, node):
        if not node in self.table.keys():
            raise ValueError("node not in graph")
        
        l = list(self.table[node].values())
        return l[0] if len(l) > 0 else 0
    
    def get_successors(self, node):
        
        if node not in self.table.keys():
            return []
        
        return list(self.table[node].keys())
    
    def get_node_max_time(self, node):
        predecessors = self.get_predecessors(node)
        if not predecessors:
            return 0
        
        return max([self.get_node_max_time(x) + self.get_node_time(x) for x in predecessors])

    def get_node_min_time(self, node):
        successors = self.get_successors(node)
        if not successors:
            return self.get_node_max_time(node)
        
        return min([self.get_node_min_time(x) for x in successors]) - self.get_node_time(node)
        
    def get_earliest_calendar(self):
                       
        return {n : self.get_node_max_time(n) for n in self.table.keys()}
        
    def get_latest_calendar(self):
        
        return {n : self.get_node_min_time(n) for n in self.table.keys()}
       
    def get_margins(self):
    
        return {n : self.get_node_min_time(n) - self.get_node_max_time(n) for n in self.table}
    
    def get_critical_nodes(self):        
        margins = self.get_margins()
        
        c = dict(filter(lambda p: p[1] == 0, margins.items())).keys()
        
        return list(c)
    
    def get_critical_path(self):
        path = {}
        
        crits = self.get_critical_nodes()
        ranks = self.get_ranks()
        for node in crits:
            successors = list(filter(lambda x: x in crits, self.get_successors(node)))
            successors.sort(key=ranks.get)# type:ignore
            path[node] = list(filter(lambda n :ranks.get(n) == ranks.get(successors[0]), successors)) if successors else []
        
        return path
    
    def get_inflection_nodes(self):
        p = self.get_critical_path()
        return sorted(list(filter(lambda n: len(p[n]) >= 2 and n != 0, p.keys())), key=self.get_ranks().get, reverse=True)
    
    def get_sub_table(self, node):
        last_node = list(self.table.keys())[-1]
        if node == last_node:
            return {last_node : self.table[last_node]}
        
        t = {}
        
        p = self.get_critical_path()
        for n in p[node]:
                t |= self.get_sub_table(n)
        
        return {node : dict(filter(lambda e: e[0] in p.keys(), self.table[node].items()))} | t
    
    
    def get_sub_graph(self, node):
        return Graph(self.get_sub_table(node))
            
    
    def get_longest_path(self):
        path = self.get_critical_path()
        inflictions = self.get_inflection_nodes()
        
        if not inflictions:
            return path

        for node in path[self.first_node]:
            l = list(self.get_sub_graph(node).get_longest_path().keys())
            filt = list(filter(lambda n: n in l, path[node]))
            path[node] = filt
            
        inflictions = self.get_inflection_nodes()
        
            
        return path
            
    
    def __str__(self) -> str:
        
        matrix: list[list[str]] = [[f"{i}"] + ['.' for _ in range(self.size)] for i in range(self.size)]
        
        for node, trans in self.table.items():           
            for _node in trans.keys():
                matrix[int(node)][int(_node)+1] = '1'
                
        return tabulate(matrix, tablefmt="rounded_grid", headers=[f"n°{self.number}"]+[str(i) for i in range(self.size)])
    
