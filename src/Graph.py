from pathlib import Path
from tabulate import tabulate

class Graph:
    
    def __init__(self, path: Path) -> None:
        with path.open() as f:
            self.data: str = f.read()
        
        self.splitted_string: list[list[str]] = [string.split(' ') for string in self.data.split('\n')]
        
        self.table: dict[str, dict[str, int]] = self._table_from_valid_list()
        
    def _table_from_valid_list(self) -> dict[str, dict[str, int]]:
        table: dict[str, dict[str, int]] = {}
                
        nodes: list[str] = [s[0] for s in self.splitted_string]
        
        # initialization of the table
        for node in nodes:
            if node not in table.keys():
                table[node] = {}

        
        table['0'] = {}
        
        size: int = len(table.keys())
        
        table[str(size)] = {}
       
        size += 1
        # We just added 2 to the size because of the the 2 new implicit states: alpha & omega
        
        all_predecessors: list[str] = self.get_all_predecessors()
        
        for line in self.splitted_string:
            
            code: str = line[0]
            predecessors: list[str] = line[2:]
            
            if not predecessors:
                table['0'] |= {code: 0}
                continue
            
            if code not in all_predecessors:
                # we subtract 2 because we added ɑ & ω
                old_size: int = size-2
                table[str(old_size)] = {str(size-1): int(self.splitted_string[old_size-1][1])}
            
            for node in predecessors:
                table[node] |= {code: int(self.splitted_string[int(node)][1])}
        
        self.size: int = len(table.keys())
        return table
    
    def get_all_predecessors(self) -> list[str]:
        predecessors: list[str] = []
        
        for line in self.splitted_string:
            predecessors += line[2:]
            
        return predecessors
    
    def has_negative_arcs(self) -> bool:
        for line in self.splitted_string:
            if int(line[1]) < 0:
                return True 
        return False
        
    def get_constraint_table(self) -> list[list[str | list[str]]]:
        return [[line[0], line[1], ', '.join(line[2:])] for line in self.splitted_string]
        
    def __str__(self) -> str:
        
        matrix: list[list[str | int]] = [[i] + ['' for _ in range(self.size)] for i in range(self.size)]
        
        for node, trans in self.table.items():           
            for _node in trans.keys():
                matrix[int(node)][int(_node)+1] = '1'
                
        return tabulate(matrix, tablefmt="rounded_grid", headers=[str(i) for i in range( self.size)])
    
g = Path("graphs/2.txt")
    
print(tabulate(Graph(g).get_constraint_table(),
               ['Code', 'Durée', 'Prédecesseurs'],
               "rounded_grid"))

print(Graph(g).has_negative_arcs())