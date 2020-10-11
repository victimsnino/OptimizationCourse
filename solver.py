import cplex
import itertools

from numpy.matrixlib.defmatrix import matrix
from utils import *
import random

def maximal_independent_set(matrix, node):
    size = matrix.shape[0]
    find_neighbours = lambda x: set([j for j in range(size) if matrix[node, j] == 1])
    neighbors = find_neighbours(node)
 
    indep_nodes = [node]
    not_neighbours = set(range(size)).difference(neighbors.union(indep_nodes))
 
    while not_neighbours:
        node = random.choice(list(not_neighbours))
        indep_nodes.append(node)
 
        not_neighbours.difference_update(find_neighbours(node).union([node])) 
 
    return indep_nodes

class Solver:
    def __init__(self, binary=True):
        self.__model = cplex.Cplex()
        self.__model.objective.set_sense(self.__model.objective.sense.maximize)
        self.__binary = binary

    def fill_from_matrix(self, matrix):
        size = matrix.shape[0]
        self.add_variables(size)

        for i in range(size):
            for j in range(i+1,size):
                if matrix[i, j] == 0:
                    self.add_constraint([j, i], '<=', 1)
            self.add_constraint(maximal_independent_set(matrix, i), '<=', 1)


    def add_variables(self, count):
        self.__model.variables.add(obj=[1]*count,
                                   lb=[0]*count, 
                                   ub=[1]*count,
                                   types=[self.__model.variables.type.binary]*count if self.__binary else "")

    def add_constraint(self, indexes_or_variables, sense, value, multiples_for_indexes=None):
        valid_operations = ["<=", ">=", "=="]
        senses = ["L", "G", "E"]
        if sense not in valid_operations:
            raise Exception("Not valid operation! %s" % sense)

        if multiples_for_indexes is None:
            multiples_for_indexes = [1]*len(indexes_or_variables)
         
        target_sense = senses[valid_operations.index(sense)]
        self.__model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indexes_or_variables,
                                                                       val=multiples_for_indexes)],
                                            senses=target_sense,
                                            rhs=[value])

    def solve(self):
        self.__model.set_results_stream(None)
        print("Start to solve")
        #self.__model.write("example.lp")
        self.__model.solve()

        values = self.__model.solution.get_values()
        
        clique_points = [index for index, val in enumerate(values) if fix_with_eps(val) > 0]
        return clique_points