from pathlib import Path
from pprint import pprint
from tabulate import tabulate
from typing import Any

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
    
    def __init__(self, number: int) -> None:
        with (Path(__file__).parent.parent / Path(f"graphs/{number}.txt")).open() as f:
            self.data: str = f.read()
            
        self.number = number
        
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
        constraint: list[list[str | list[str]]] = [[k] + [str(e) for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        deleted_nodes: list[str] = []
        ranks = {}
                
        for i in range(len(constraint)):
            
            for line in constraint:
                _line: list[str | list[str]] = line[:2] + [list(filter(lambda x: x not in deleted_nodes, line[2]))]

                if _line[2]:
                    continue
                
                ranks[line[0]] = i
                constraint.remove(line)
                deleted_nodes.append(line[0]) # type: ignore
                break
            
        return ranks
        
    def __str__(self) -> str:
        
        matrix: list[list[str]] = [[f"{i}"] + ['.' for _ in range(self.size)] for i in range(self.size)]
        
        for node, trans in self.table.items():           
            for _node in trans.keys():
                matrix[int(node)][int(_node)+1] = '1'
                
        return tabulate(matrix, tablefmt="rounded_grid", headers=[f"n°{self.number}"]+[str(i) for i in range(self.size)])
    
