from solver import Solver
import networkx as nx
import matplotlib.pyplot as plt 

class SolveAndVizualize:
    def __init__(self):
        self.__solver = Solver()
        self.__G = nx.Graph()

    def add_edge(self, x, y):
        self.__G.add_edge(x, y)

    def solve(self):
        self.__solver.solve()

        plt.figure(figsize=(8,8))
        nx.draw(self.__G, connectionstyle='arc3, rad = 0.1')
        plt.show()


t = SolveAndVizualize()
t.add_edge(1, 2)
t.add_edge(1, 3)
t.add_edge(2, 3)

t.add_edge(4, 1)
t.add_edge(5, 2)
t.add_edge(6, 3)

t.solve()