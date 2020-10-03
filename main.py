from solver import Solver
import networkx as nx
import matplotlib.pyplot as plt 
import numpy as np

class SolveAndVizualize:
    def __init__(self):
        self.__solver = Solver()
        self.__G = nx.Graph()

    def add_edge(self, x, y):
        self.__G.add_edge(x, y)

    def __add_constrains_to_graph(self):
        nodes = np.array(self.__G.nodes)
        for i, node in enumerate(nodes):
            for another_node in nodes[i+1:]:
                if self.__G.has_edge(node, another_node) == False:
                    self.__solver.add_constraint([str(node), str(another_node)], '<=', 1)

    def solve(self):
        for node in self.__G.nodes:
            self.__solver.add_variable(str(node))
        
        self.__add_constrains_to_graph()
        values, clique_points = self.__solver.solve()

        plt.figure(figsize=(8,8))
        nx.draw(self.__G, with_labels=True, node_color=values, connectionstyle='arc3, rad = 0.1')
        plt.show()
        return clique_points


t = SolveAndVizualize()
t.add_edge(1, 2)
t.add_edge(1, 3)
t.add_edge(2, 3)

t.add_edge(4, 1)
t.add_edge(5, 2)
t.add_edge(6, 3)

t.solve()