import cplex

from numpy.matrixlib.defmatrix import matrix
from utils import *
import random

# Find maximal independent set for target node. Moreover, 
# it search's only in rest part of matrix
# (not 0..n, 0..n, but in node...n, node...n matrix)
def maximal_independent_set(matrix, input_node):
    available_nodes = range(input_node,matrix.shape[0])
    node = input_node
    find_neighbours = lambda x: set([j for j in available_nodes if matrix[x, j] == 1])
    neighbors = find_neighbours(node)
 
    indep_nodes = [node]
    not_neighbours = set(available_nodes).difference(neighbors.union(indep_nodes))
 
    while not_neighbours:
        node = random.choice(list(not_neighbours))
        indep_nodes.append(node)
 
        not_neighbours.difference_update(find_neighbours(node).union([node])) 
 
    return indep_nodes

class Solver:
    def __init__(self, binary=True, independent_set =True):
        self.__model = cplex.Cplex()
        self.__model.objective.set_sense(self.__model.objective.sense.maximize)
        self.__binary = binary
        self.__independent_set = independent_set

    def fill_from_matrix(self, matrix):
        size = matrix.shape[0]
        self.add_variables(size)

        max_degree = 0
        for i in range(size):
            temp_degree = 0
            for j in range(i+1,size):
                if matrix[i, j] == 0:
                    self.add_constraint([j, i], '<=', 1)
                else:
                    temp_degree += 1
            max_degree = max((max_degree, temp_degree))

            if self.__independent_set:
                self.add_constraint(maximal_independent_set(matrix, i), '<=', 1)

        # count of nodes in clique can't be more, than max degree
        self.add_constraint(list(range(size)), '<=', max_degree)

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
        return self.__model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indexes_or_variables,
                                                                              val=multiples_for_indexes)],
                                                   senses=target_sense,
                                                   rhs=[value])

    def remove_constraint(self, index_of_constraint):
        self.__model.linear_constraints.delete(index_of_constraint)

    def solve(self):
        self.__model.set_results_stream(None)
        #print("Start to solve")
        #self.__model.write("example.lp")
        self.__model.solve()

        values = self.__model.solution.get_values()
        if self.__binary:
            clique_points = [index for index, val in enumerate(values) if fix_with_eps(val) == 1]
            return clique_points
        else:
            return values
