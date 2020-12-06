import cplex
from networkx.algorithms.bipartite.basic import color
from utils import *
import copy
import networkx as nx
import operator

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
        node = list(not_neighbours)[0]
        indep_nodes.append(node)
 
        not_neighbours.difference_update(find_neighbours(node).union([node])) 
 
    return indep_nodes

def find_all_independent_sets(input_matrix, input_node):
    sets = []
    new_set = []
    matrix = copy.deepcopy(input_matrix)
    while(True):
        for node in new_set:
            if node != input_node:
                matrix[node, input_node] = 1
                matrix[input_node, node] = 1
        new_set = maximal_independent_set(matrix, input_node)
        if len(new_set) <= 1:
            break
        sets.append(sorted(new_set))
    
    return sets

def maximal_degree_that_potentially_can_be_size_of_clique(matrix):
    graph = nx.from_numpy_matrix(matrix)
    coloring = nx.algorithms.coloring.greedy_color(graph)
    max_color= max(coloring.items(), key=operator.itemgetter(1))[1]
    return max_color+1
    
class Solver:
    def __init__(self, binary=True, independent_set =True, max = True):
        self.__model = cplex.Cplex()
        self.__max = max
        self.__model.objective.set_sense(self.__model.objective.sense.maximize if max else self.__model.objective.sense.minimize)
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
                for ind_set in find_all_independent_sets(matrix, i):
                    self.add_constraint(ind_set, '<=', 1)

        # count of nodes in clique can't be more, than max degree
        self.add_constraint(list(range(size)), '<=', max_degree)
        self.add_constraint(list(range(size)), '<=', maximal_degree_that_potentially_can_be_size_of_clique(matrix))

    def add_variables(self, count,obj=1, ub=None):
        return self.__model.variables.add(obj=[obj]*count,
                                   lb=[0]*count, 
                                   ub=[ub]*count if ub else None,
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

    def pop_constraint(self):
        self.remove_constraint(self.__model.linear_constraints.get_num()-1)

    def set_coefficent_for_constraint(self, constraint_id, variable, coefficient):
        self.__model.linear_constraints.set_linear_components(constraint_id, [[variable], [coefficient]])

    def remove_constraint(self, index_of_constraint):
        self.__model.linear_constraints.delete(index_of_constraint)

    def solve(self, return_raw_values = False):
        self.__model.set_results_stream(None)
        #print("Start to solve")
        #self.__model.write("example.lp")
        self.__model.solve()

        values = self.__model.solution.get_values()
        if self.__model.solution.get_status() == 3: #infeasible
            values = [0 if self.__max else 1]*len(values)
        if self.__binary and not return_raw_values:
            clique_points = [index for index, val in enumerate(values) if fix_with_eps(val) == 1]
            return clique_points
        else:
            return values
