from pathlib import Path
from typing import Any
from tabulate import tabulate

class Graph:
    def __init__(self, table: dict[int, dict[int, int]]) -> None:

        self.table: dict[int, dict[int, int]] = table.copy()
        self.number: int = 0
        self.size: int = len(table.keys())
        self.first_node: int = list(sorted(self.table.keys()))[0]
        
        self.has_circuit: bool = self.has_circuit_by_deletions()[0]
        self.negative_arcs: bool = self.has_negative_arcs()
        
        self.ranks: dict[int, int] = self.get_ranks() if not self.has_circuit and not self.negative_arcs else {}
        
    @classmethod
    def from_file(cls, number: int = 0, path: str = "", string_override= False) -> "Graph":
        """The interface enabling the possibility to load a graph from a file or from a string.

        Keyword Arguments:
            number -- The number from the list of given test graphs (default: {0})
            path -- The alternative file path or the string content to load the graph from  (default: {""})
            string_override -- A boolean to choose between file loading or string loading. (default: {False})

        Returns:
            The derived graph.
        """

        if (string_override):
            data = path
        elif (path == ""):
            with (Path(__file__).parent.parent / Path(f"graphs/F3_{number}.txt")).open() as f:
                data: str = f.read()
            number = number
        else:
            with Path(path).open() as f:
                data: str = f.read()


        filtered = lambda s: list(filter(lambda x: x, s))
        splitted_data: list[str] = filtered(data.split('\n'))

        splitted_string: list[list[int]] = [[int(i) for i in filtered(string.split(' '))] for string in splitted_data]

        table: dict[int, dict[int, int]] = cls.table_from_valid_list(splitted_string)

        g = Graph(table)

        g.number = number

        return g

    def to_dot_format(self, highlight_critical_path: bool =False) -> str:
        """Transforms the graph to the dot format to render it graphically.

        Keyword Arguments:
            highlight_critical_path -- Should the longest path be colored in red (default: {False})

        Returns:
            The resulting dot formate string.
        """
        to_dot = "digraph { rankdir=LR\n"

        crit: list[int] = []
        path = {}
        if highlight_critical_path:
            crit = self.get_critical_nodes()
            path = self.get_longest_path()
            for n in crit:
                to_dot += f'    "{n}" [color="red" label="{n}"]\n'

        for node, succs in self.table.items():
            for k, v in succs.items():
                to_dot += f'    "{node}" -> "{k}" [label="{v}"'

                if k in crit and node == 0:
                    to_dot += ' color="red"'

                if path.get(node) and k in path[node]: # in crit and k in crit:
                    to_dot += ' color="red"'

                to_dot +=' ]\n'

        to_dot += "}"
        return to_dot

    @classmethod
    def table_from_valid_list(cls, splitted_string: list[list[int]]) -> dict[int, dict[int, int]]:
        """Generates a table representing the graph from the format given by the projects subject.

        Arguments:
            splitted_string -- The arrayized raw data from the file. Must be valid format, no verification are done.

        Returns:
            The graphs table in this form :
            {
                node_n: {
                    node_k: time,
                    node_k2: time,
                    node_k3: time
                },
                node_n+1: {
                    node_k: time,
                },
                ...
            }
        """

        table: dict[int, dict[int, int]] = {}

        nodes: list[int] = [int(s[0]) for s in splitted_string]


        table[0] = {}

        # initialization of the table
        for node in nodes:
            if node not in table.keys():
                table[node] = {}

        last_node: int = len(table.keys())

        table[last_node] = {}

        def get_all_predecessors(splitted_string) -> list[int]:
            """Gets a list of all the nodes that are predecessors."""
            predecessors: list[int] = []

            for line in splitted_string:
                predecessors += line[2:]

            return list(set(predecessors))

        all_predecessors: list[int] = get_all_predecessors(splitted_string)

        for line in splitted_string:

            label: int = line[0]
            predecessors: list[int] = line[2:]

            # Entrees case
            if not predecessors:
                table[0] |= {label: 0}
                continue

            # Exits case
            if label not in all_predecessors:
                table[label] = {last_node: splitted_string[label-1][1]}

            # Commun case
            for node in predecessors:
                table[node] |= {label: splitted_string[node-1][1]}

        return table

    def get_sub_table(self, node) ->  dict[int, dict[int, int]]:
        """Gets part of the table concerning the given node and any critical node leading to the exit node.

        Arguments:
            node -- The given node.

        Returns:
            The extracted sub table.
        """
        last_node: int = list(self.table.keys())[-1]
        if node == last_node:
            return {last_node : self.table[last_node]}

        sub_table = {}

        critical_path: dict[int, list[int]] = self.get_critical_path()
        for n in critical_path[node]:
            sub_table |= self.get_sub_table(n)

        return {node : dict(filter(lambda e: e[0] in critical_path.keys(), self.table[node].items()))} | sub_table

    def get_sub_graph(self, node: int) -> "Graph":
        """Gets the subgraph from the node's sub-table.

        Arguments:
            node -- The given node.

        Returns:
            The new graph.
        """
        return Graph(self.get_sub_table(node))

    def has_negative_arcs(self) -> bool:
        """
        Returns:
            Whether or not the graph has negative arcs
        """
        for line in self.table.values():
            for value in line.values():
                if value < 0:
                    return True
        return False

    def get_matrix(self) -> list[list[int]]:
        """
        Returns:
            The graph in matrix form.
        """
        matrix: list[list[int]] = [[] for _ in range(self.size)]

        for i, v in enumerate(self.table.values()):

            matrix[i] = [1 if i in v.keys() else 0 for i in range(self.size)]

        return matrix

    def get_value_matrix(self) -> list[list[str]]:
        """
        Returns:
            The graph in matrix form with values.
        """
        matrix: list[list[str]] = [[] for _ in range(self.size)]

        for k, v in self.table.items():
            matrix[k] = [str(v[i]) if i in v.keys() else '' for i in range(self.size)]

        return matrix

    def get_predecessors(self, node: int) -> list[int]:
        """Retrieves the list of predecessors of a given node. 

        Arguments:
            node -- The given node

        Returns:
            The list of predecessors.
        """

        if node not in self.table.keys():
            return []

        predecessors: list[int] = []
        
        for label, successors in self.table.items():
            if node in successors.keys():
                predecessors.append(label)

        return list(set(predecessors))

    def get_successors(self, node: int) -> list[int]:
        """Retrieves the list of successors of a given node. 
        
        Arguments:
            node -- The given node.

        Returns:
            A list of successors of the node.
        """
        if node not in self.table.keys():
            return []

        return list(self.table[node].keys())

    def get_constraint_table(self) -> dict[int, dict[int, list[int]]]:
        """
        Returns:
            The original constraint data in table form.
        """
        constraints: dict[int, dict[int, list[int]]] = {}
        key: int

        for node, successors in self.table.items():
            
            if time := list(successors.values()):
                key = time[0]
            else:
                key = 0
                
            constraints[node] = {key: self.get_predecessors(node)}

        return constraints

    def has_circuit_by_deletions(self, step:bool = False) -> tuple[bool, list[Any]]:
        """Checks circuits by deleting entrees successively.

        Keyword Arguments:
            step -- The different steps of deletion (default: {False})

        Returns:
            Whether or not the graph has at least one circuit.
        """
        steps: list[Any] = []

        constraint: list[list[Any]] = [[k] + [e for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        deleted_nodes: list[int] = []

        while (len(constraint) > 0):
            is_impossible = 0
            intermediate_step = []

            for line in constraint:

                label: int = line[0]
                predecessors: int = line[2]

                if predecessors:
                    is_impossible += 1
                    continue

                deleted_nodes.append(label)

                if step:
                    intermediate_step.append(label)

            if step:
                steps.append(intermediate_step.copy())

            if is_impossible == len(constraint):
                return True, steps

            # filter out deleted nodes lines
            constraint = list(filter(lambda l: l[0] not in deleted_nodes, constraint))

            # filter out the deleted nodes in any predecessors list            
            constraint = [line[:2] + [list(filter(lambda x: x not in deleted_nodes, line[2]))] for line in constraint]

        return False, steps

    def get_ranks(self) -> dict[int, int]:
        """
        Returns:
            Ranks of all the node in the graph.
        """
        constraint: list[list[Any]] = [[k] + [e for e in v.keys()] + list(v.values()) for k,v in self.get_constraint_table().items()]
        deleted_nodes: list[int] = []
        ranks: dict[int, int] = {}

        current_rank = 0
        while (len(constraint) > 0):

            for line in constraint:

                label: int = line[0]
                predecessors: int = line[2]
                
                if predecessors:
                    continue

                ranks[label] = current_rank
                deleted_nodes.append(label)

            # filter out deleted nodes lines
            constraint = list(filter(lambda l: l[0] not in deleted_nodes, constraint))
            
            # filter out the deleted nodes in any predecessors list
            constraint = [line[:2] + [list(filter(lambda x: x not in deleted_nodes, line[2]))] for line in constraint]

            current_rank +=1

        return ranks

    def get_node_time(self, node: int) -> int:
        """Gets the given node's duration.

        Arguments:
            node -- The given node.

        Raises:
            ValueError: if the node is not in the graph.

        Returns:
            The value of arcs originating from the given node.
        """
        if not node in self.table.keys():
            raise ValueError("node not in graph")

        l = list(self.table[node].values())
        return l[0] if len(l) > 0 else 0

    def get_node_earliest_date(self, node: int) -> int:
        """Gets the nodes earliest date.

        Arguments:
            node -- The given node.

        Returns:
            The earliest date of the given node.
        """
        predecessors: list[int] = self.get_predecessors(node)
        
        if not predecessors:
            return 0

        # max(t_i + d_i)
        return max([self.get_node_earliest_date(x) + self.get_node_time(x) for x in predecessors])

    def get_node_latest_date(self, node: int) -> int:
        """Gets the nodes latest date.

        Arguments:
            node -- The given node.

        Returns:
            The latest date of the given node.
        """
        successors: list[int] = self.get_successors(node)
        
        if not successors:
            return self.get_node_earliest_date(node)

        # min(t_i) - d_i
        return min([self.get_node_latest_date(x) for x in successors]) - self.get_node_time(node)

    def get_node_free_margin(self, node: int) -> int:
        """Gets the free margin of a given node.
        
        Arguments:
            node -- The given node.

        Returns:
            The free margin associated with the given node. 
        """
        successors: list[int] = self.get_successors(node)
        
        if not successors:
            return self.get_node_earliest_date(node)
        
        node_early: int = self.get_node_earliest_date(node)
        node_time: int = self.get_node_time(node)

        # min(t_j - (t_i + d_i))
        return min([self.get_node_earliest_date(x) - (node_early + node_time) for x in successors])

    def get_earliest_calendar(self) -> dict[int, int]:

        return {n : self.get_node_earliest_date(n) for n in self.table.keys()}

    def get_latest_calendar(self) -> dict[int, int]:

        return {n : self.get_node_latest_date(n) for n in self.table.keys()}

    def get_total_margins(self) -> dict[int, int]:

        return {n : self.get_node_latest_date(n) - self.get_node_earliest_date(n) for n in self.table}

    def get_free_margins(self) -> dict[int, int]:

        return {n : self.get_node_free_margin(n) for n in self.table}

    def get_critical_nodes(self) -> list[int]:
        """Gets all the nodes in the critical path.

        Returns:
            A dictionary of all the nodes in the critical path.
        """
        margins: dict[int, int] = self.get_total_margins()

        # we just keep the nodes with a margin equal to 0.
        nodes: list[int] = list(dict(filter(lambda pair: pair[1] == 0, margins.items())).keys())

        return nodes

    def get_critical_path(self) -> dict[int, list[int]]:
        """Gets the naive path connecting all the critical nodes.

        Returns:
            A dictionary of nodes and where they lead. 
        """
        critical_path: dict[int, list[int]] = {}

        critical_nodes: list[int] = self.get_critical_nodes()
        ranks: dict[int, int] = self.ranks
        
        for node in critical_nodes:
            successors = list(filter(lambda x: x in critical_nodes, self.get_successors(node)))
            successors.sort(key=ranks.get)
            # we prioritize the lesser rank.
            critical_path[node] = list(filter(lambda node: ranks.get(node) == ranks.get(successors[0]), successors)) if successors else []

        return critical_path

    def get_inflection_nodes(self) -> list[int]:
        """Gets all the nodes in the critical path that have two or more outputs excluding the first node.

        Returns:
            The list of all the nodes that point to more than 1 node.
        """
        critical_path: dict[int, list[int]] = self.get_critical_path()
        filter_func = lambda node: len(critical_path[node]) >= 2 and node != self.first_node
        return list(filter(filter_func, critical_path.keys()))

    def get_longest_path(self) -> dict[int, list[int]]:
        """Gets the longest possible path in the graph.
        
        Because our algorithm just gives us the nodes that compose the critical path and not the path.
        We filter the critical path, it just makes the naive connexion between critical nodes.
        The only tuning it does is prioritizing the smaller rank nodes, for obvious reasons.
        
        Here we find the nodes that can have a faulty connexion, and we verify if it should really be here.
        For that, we simply isolate the node and create the sub-graph associated, then, we figure out the longest path of this new graph.
        
        Finally, we filter out the nodes(in the list of successors nodes in the critical path) that aren't in the longest path.

        Returns:
            A dictionary of nodes and where they head to in the longest path.
        """
        path: dict[int, list[int]] = self.get_critical_path()
        inflictions: list[int] = self.get_inflection_nodes()

        if not inflictions:
            return path

        for node in inflictions:
            sub_longest: dict[int, list[int]] = self.get_sub_graph(node).get_longest_path()
            path[node] = list(filter(lambda n: n in sub_longest.keys(), path[node]))

        return path

    def __str__(self) -> str:

        matrix: list[list[str]] = [[f"{i}"] + ['.' for _ in range(self.size)] for i in range(self.size)]

        for node, trans in self.table.items():
            for _node in trans.keys():
                matrix[int(node)][int(_node)+1] = '1'

        return tabulate(matrix, tablefmt="rounded_grid", headers=[f"n°{self.number}"]+[str(i) for i in range(self.size)])

