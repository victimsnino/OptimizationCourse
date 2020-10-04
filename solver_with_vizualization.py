from solver import Solver
import networkx as nx
import matplotlib.pyplot as plt 
import numpy as np

class SolveAndVizualize:
    def __init__(self, vizualize = True):
        self.__solver = Solver()
        self.__G = nx.Graph()
        self.__vizualize = vizualize

    def add_edge(self, x, y):
        self.__G.add_edge(x, y)

    def add_post_constrains_to_graph(self):
        for node in self.__G.nodes:
            self.__solver.add_variable(str(node))

        nodes = np.array(self.__G.nodes)
        for i, node in enumerate(nodes):
            for another_node in nodes[i+1:]:
                if self.__G.has_edge(node, another_node) == False:
                    self.__solver.add_constraint([str(node), str(another_node)], '<=', 1)

    def ban_node(self, node):
        self.__solver.add_constraint([node], '==', 0)

    def solve(self):       
        values, clique_points = self.__solver.solve()
        
        if self.__vizualize:
            plt.figure(figsize=(8,8))
            nx.draw(self.__G, with_labels=True, node_color=values, connectionstyle='arc3, rad = 0.1')
            plt.show()

        return [str(v) for v in sorted([int(v) for v in clique_points])]